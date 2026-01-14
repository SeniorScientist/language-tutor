"""RAG Service using ChromaDB and sentence-transformers."""

import logging
from typing import Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from config import Settings, get_settings

logger = logging.getLogger(__name__)


class RAGService:
    """RAG (Retrieval Augmented Generation) service.

    Uses ChromaDB for vector storage and sentence-transformers for embeddings.
    All operations run on CPU - no GPU required.
    """

    # Collection names
    GRAMMAR_RULES = "grammar_rules"
    VOCABULARY = "vocabulary"
    EXAMPLES = "examples"

    def __init__(self, settings: Settings):
        """Initialize RAG service.

        Args:
            settings: Application settings.
        """
        self.settings = settings
        self._embedding_model: Optional[SentenceTransformer] = None
        self._client: Optional[chromadb.Client] = None

        # Initialize ChromaDB
        self._init_chromadb()

        # Initialize embedding model
        self._init_embedding_model()

        # Seed initial data if collections are empty
        self._seed_data()

        logger.info("RAG service initialized")

    def _init_chromadb(self):
        """Initialize ChromaDB client and collections."""
        persist_dir = Path(self.settings.chroma_persist_directory)
        persist_dir.mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Create or get collections
        self._grammar_collection = self._client.get_or_create_collection(
            name=self.GRAMMAR_RULES,
            metadata={"description": "Grammar rules and explanations"},
        )

        self._vocabulary_collection = self._client.get_or_create_collection(
            name=self.VOCABULARY,
            metadata={"description": "Vocabulary words and definitions"},
        )

        self._examples_collection = self._client.get_or_create_collection(
            name=self.EXAMPLES, metadata={"description": "Example sentences and usage"}
        )

        logger.info(f"ChromaDB initialized at: {persist_dir}")

    def _init_embedding_model(self):
        """Initialize the sentence-transformer embedding model."""
        logger.info(f"Loading embedding model: {self.settings.embedding_model}")
        self._embedding_model = SentenceTransformer(
            self.settings.embedding_model,
            device="cpu",  # Force CPU - works everywhere
        )
        logger.info("Embedding model loaded")

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.
        """
        embeddings = self._embedding_model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def _seed_data(self):
        """Seed initial grammar rules and examples if empty."""
        # Check if already seeded
        if self._grammar_collection.count() > 0:
            logger.info("Collections already seeded, skipping")
            return

        logger.info("Seeding initial data...")

        # Grammar rules for supported languages (English, Chinese, Russian, Japanese)
        grammar_rules = [
            # English (E-E: explaining complex English in simple English)
            {
                "id": "en_phrasal_verbs",
                "language": "English",
                "content": "Phrasal verbs are verbs combined with prepositions or adverbs that create new meanings. 'Give up' means to stop trying. 'Look after' means to take care of. 'Put off' means to delay. The meaning often can't be guessed from the individual words. Example: 'I had to put off the meeting' means I had to delay it.",
            },
            {
                "id": "en_conditionals",
                "language": "English",
                "content": "Conditionals express 'if...then' situations. Zero conditional (facts): 'If you heat water, it boils.' First conditional (likely future): 'If it rains, I will stay home.' Second conditional (unlikely): 'If I won the lottery, I would travel.' Third conditional (past unreal): 'If I had studied, I would have passed.'",
            },
            {
                "id": "en_articles",
                "language": "English",
                "content": "Use 'a' before consonant sounds ('a book'), 'an' before vowel sounds ('an apple'). Use 'the' for specific things both speaker and listener know ('the sun', 'the book you mentioned'). No article for general plurals ('Dogs are friendly') or abstract concepts ('Love is important').",
            },
            {
                "id": "en_tenses",
                "language": "English",
                "content": "Present simple (habits): 'I work every day.' Present continuous (now): 'I am working.' Past simple (finished): 'I worked yesterday.' Present perfect (past connected to now): 'I have worked here for 5 years.' Past perfect (before another past event): 'I had already eaten when she arrived.'",
            },
            {
                "id": "en_confusing_pairs",
                "language": "English",
                "content": "Common confusing words: affect (verb) vs effect (noun): 'The rain affects my mood' vs 'The effect is clear.' Their (possession) vs there (place) vs they're (they are). Its (belonging to it) vs it's (it is). Your (belonging to you) vs you're (you are).",
            },
            {
                "id": "en_passive_voice",
                "language": "English",
                "content": "Passive voice puts focus on the action, not who does it. Active: 'The chef cooked the meal.' Passive: 'The meal was cooked (by the chef).' Form: be + past participle. Use passive when the doer is unknown, unimportant, or obvious. 'The window was broken.' 'English is spoken worldwide.'",
            },
            {
                "id": "en_prepositions",
                "language": "English",
                "content": "Prepositions show relationships. Time: at (specific time: at 3pm), on (days: on Monday), in (longer periods: in March, in 2024). Place: at (point: at the door), on (surface: on the table), in (enclosed: in the box). Movement: to (destination), into (entering), onto (surface).",
            },
            {
                "id": "en_idioms",
                "language": "English",
                "content": "Idioms are expressions with non-literal meanings. 'Break the ice' = start a conversation. 'Piece of cake' = very easy. 'Hit the nail on the head' = exactly right. 'Under the weather' = feeling sick. 'Cost an arm and a leg' = very expensive. Learn them as fixed phrases.",
            },
            # Chinese (Mandarin)
            {
                "id": "zh_tones",
                "language": "Chinese",
                "content": "Chinese has 4 main tones plus a neutral tone. First tone (ˉ): high and flat (mā 妈 = mother). Second tone (ˊ): rising (má 麻 = hemp). Third tone (ˇ): falling-rising (mǎ 马 = horse). Fourth tone (ˋ): falling (mà 骂 = scold). Wrong tones change meaning completely!",
            },
            {
                "id": "zh_sentence_structure",
                "language": "Chinese",
                "content": "Chinese basic word order is Subject-Verb-Object (SVO) like English. 我吃饭 (Wǒ chī fàn) = I eat rice. Time and location come before the verb: 我今天在家吃饭 (I today at-home eat-rice). Question words stay in place: 你吃什么？(You eat what?) = What do you eat?",
            },
            {
                "id": "zh_measure_words",
                "language": "Chinese",
                "content": "Chinese uses measure words (量词) between numbers and nouns. 一个人 (yī gè rén) = one person (个 is general). 一本书 (yī běn shū) = one book (本 for books). 一只猫 (yī zhī māo) = one cat (只 for animals). Each noun category has specific measure words.",
            },
            {
                "id": "zh_aspect_particles",
                "language": "Chinese",
                "content": "Chinese uses particles instead of verb conjugation to show tense/aspect. 了 (le): completed action (我吃了 = I ate). 过 (guò): past experience (我吃过 = I have eaten before). 着 (zhe): ongoing state (他坐着 = he is sitting). 在 (zài): in progress (我在吃 = I am eating).",
            },
            {
                "id": "zh_ba_structure",
                "language": "Chinese",
                "content": "The 把 (bǎ) structure emphasizes what happens to an object. Pattern: Subject + 把 + Object + Verb + Result. 我把书放在桌子上 (I BA book put on table) = I put the book on the table. Used when the action changes the object's state or position.",
            },
            # Russian
            {
                "id": "ru_cases",
                "language": "Russian",
                "content": "Russian has 6 grammatical cases. Nominative (subject): кто? что? Genitive (possession, 'of'): кого? чего? Dative (indirect object, 'to'): кому? чему? Accusative (direct object): кого? что? Instrumental ('with/by'): кем? чем? Prepositional ('about/in'): о ком? о чём? Each case has different noun endings.",
            },
            {
                "id": "ru_verb_aspect",
                "language": "Russian",
                "content": "Russian verbs have two aspects: imperfective (incomplete/repeated) and perfective (complete/single). читать (imperfective) = to read/be reading. прочитать (perfective) = to finish reading. Я читал книгу (I was reading) vs Я прочитал книгу (I finished reading). Most verbs come in pairs.",
            },
            {
                "id": "ru_gender",
                "language": "Russian",
                "content": "Russian nouns have three genders. Masculine: usually end in consonant (стол = table). Feminine: usually end in -а/-я (книга = book). Neuter: usually end in -о/-е (окно = window). Adjectives must agree: красивый дом (beautiful house-m), красивая машина (beautiful car-f), красивое небо (beautiful sky-n).",
            },
            {
                "id": "ru_motion_verbs",
                "language": "Russian",
                "content": "Russian has paired motion verbs: one for going somewhere specific (definite), one for general motion (indefinite). идти/ходить = go on foot. ехать/ездить = go by vehicle. Я иду в школу (I'm going to school now) vs Я хожу в школу (I go to school regularly).",
            },
            {
                "id": "ru_no_articles",
                "language": "Russian",
                "content": "Russian has no articles (a, an, the). Context determines if something is specific or general. Кот спит = A cat sleeps / The cat sleeps. Word order and demonstratives help clarify: Этот кот (this cat = the cat). Какой-то кот (some cat = a cat).",
            },
            # Japanese
            {
                "id": "ja_writing_systems",
                "language": "Japanese",
                "content": "Japanese uses three writing systems. Hiragana (ひらがな): native words, grammar. Katakana (カタカナ): foreign words, emphasis. Kanji (漢字): Chinese characters for meaning. Example: 私はコーヒーを飲みます (I drink coffee) uses all three: 私/飲 (kanji), は/を/みます (hiragana), コーヒー (katakana).",
            },
            {
                "id": "ja_particles",
                "language": "Japanese",
                "content": "Japanese particles mark grammar roles. は (wa): topic marker (私は = as for me). が (ga): subject marker (犬がいる = there is a dog). を (wo): object marker (本を読む = read a book). に (ni): direction/time (学校に行く = go to school). で (de): location of action (家で食べる = eat at home).",
            },
            {
                "id": "ja_verb_forms",
                "language": "Japanese",
                "content": "Japanese verbs conjugate but don't change for person/number. Basic forms: dictionary form (食べる taberu), masu form (食べます tabemasu - polite), te form (食べて tabete - connecting), nai form (食べない tabenai - negative). Verbs come at sentence end.",
            },
            {
                "id": "ja_keigo",
                "language": "Japanese",
                "content": "Keigo (敬語) is Japanese honorific language. Three levels: Teineigo (丁寧語): polite (-ます forms). Sonkeigo (尊敬語): respect for others' actions (いらっしゃる instead of いる). Kenjougo (謙譲語): humble your own actions (参る instead of 行く). Essential for business and formal situations.",
            },
            {
                "id": "ja_sentence_structure",
                "language": "Japanese",
                "content": "Japanese word order is SOV (Subject-Object-Verb). English: I eat sushi. Japanese: 私は寿司を食べます (I sushi eat). Modifiers come before what they modify. The verb always comes at the end. Questions add か (ka) at the end: 食べますか？(Do you eat?)",
            },
            {
                "id": "ja_counters",
                "language": "Japanese",
                "content": "Japanese uses counters for counting different objects. 人 (nin): people (三人 = 3 people). 本 (hon): long objects (二本 = 2 pens). 匹 (hiki): small animals (四匹 = 4 cats). 枚 (mai): flat objects (五枚 = 5 papers). 個 (ko): general counter. Numbers change pronunciation with some counters.",
            },
            # General
            {
                "id": "gen_writing_systems",
                "language": "General",
                "content": "Different writing systems: Alphabets (Latin, Cyrillic) where letters represent sounds. Syllabaries (Japanese kana) where symbols represent syllables. Logographic (Chinese) where characters represent meanings. Russian uses Cyrillic (33 letters). Japanese combines all three types.",
            },
            {
                "id": "gen_word_order",
                "language": "General",
                "content": "Main word orders in languages: SVO (Subject-Verb-Object): English, Chinese. SOV (Subject-Object-Verb): Japanese. Russian is flexible but commonly SVO. Word order affects how you construct sentences and think in the language.",
            },
        ]

        # Add grammar rules
        self._grammar_collection.add(
            ids=[r["id"] for r in grammar_rules],
            documents=[r["content"] for r in grammar_rules],
            metadatas=[{"language": r["language"]} for r in grammar_rules],
            embeddings=self._embed([r["content"] for r in grammar_rules]),
        )

        # Example sentences for all 4 languages
        examples = [
            # English examples (complex → simple explanations)
            {
                "id": "ex_en_1",
                "language": "English",
                "content": "'I've been working here for 5 years' - Present perfect continuous. Shows an action that started in the past and continues now. Simple: I started 5 years ago and I still work here.",
            },
            {
                "id": "ex_en_2",
                "language": "English",
                "content": "'If I had known, I would have helped' - Third conditional (past unreal). Simple: I didn't know, so I didn't help. But imagine I knew - then I would help.",
            },
            {
                "id": "ex_en_3",
                "language": "English",
                "content": "'The report was submitted by the team' - Passive voice. The focus is on 'the report', not who did it. Active version: 'The team submitted the report.'",
            },
            {
                "id": "ex_en_4",
                "language": "English",
                "content": "'She came up with a great idea' - Phrasal verb 'come up with' = think of, invent. Simple: She thought of a great idea.",
            },
            # Chinese examples
            {
                "id": "ex_zh_1",
                "language": "Chinese",
                "content": "你好，你叫什么名字？(Nǐ hǎo, nǐ jiào shénme míngzi?) - Hello, what is your name? Basic greeting and introduction.",
            },
            {
                "id": "ex_zh_2",
                "language": "Chinese",
                "content": "我想要一杯咖啡。(Wǒ xiǎng yào yī bēi kāfēi.) - I want a cup of coffee. 想要 = want, 一杯 = one cup (measure word), 咖啡 = coffee.",
            },
            {
                "id": "ex_zh_3",
                "language": "Chinese",
                "content": "他在学校学习中文。(Tā zài xuéxiào xuéxí zhōngwén.) - He studies Chinese at school. 在 indicates location of action.",
            },
            {
                "id": "ex_zh_4",
                "language": "Chinese",
                "content": "我把书放在桌子上了。(Wǒ bǎ shū fàng zài zhuōzi shàng le.) - I put the book on the table. 把 structure for disposal.",
            },
            # Russian examples
            {
                "id": "ex_ru_1",
                "language": "Russian",
                "content": "Привет! Как дела? (Privet! Kak dela?) - Hi! How are you? Informal greeting among friends.",
            },
            {
                "id": "ex_ru_2",
                "language": "Russian",
                "content": "Я хочу заказать кофе. (Ya khochu zakazat' kofe.) - I want to order coffee. хочу = I want, заказать = to order (perfective).",
            },
            {
                "id": "ex_ru_3",
                "language": "Russian",
                "content": "Я читаю интересную книгу. (Ya chitayu interesnuyu knigu.) - I am reading an interesting book. Accusative case for direct object.",
            },
            {
                "id": "ex_ru_4",
                "language": "Russian",
                "content": "Я еду на работу на автобусе. (Ya yedu na rabotu na avtobuse.) - I'm going to work by bus. еду = definite motion verb (going now).",
            },
            # Japanese examples
            {
                "id": "ex_ja_1",
                "language": "Japanese",
                "content": "はじめまして。田中です。(Hajimemashite. Tanaka desu.) - Nice to meet you. I'm Tanaka. Standard self-introduction.",
            },
            {
                "id": "ex_ja_2",
                "language": "Japanese",
                "content": "コーヒーを一つください。(Kōhī o hitotsu kudasai.) - One coffee, please. を marks object, ください = please give me.",
            },
            {
                "id": "ex_ja_3",
                "language": "Japanese",
                "content": "駅はどこですか？(Eki wa doko desu ka?) - Where is the station? は marks topic, か makes it a question.",
            },
            {
                "id": "ex_ja_4",
                "language": "Japanese",
                "content": "昨日、友達と映画を見ました。(Kinō, tomodachi to eiga o mimashita.) - Yesterday, I watched a movie with a friend. と = with, を = object marker, ました = past polite.",
            },
        ]

        self._examples_collection.add(
            ids=[e["id"] for e in examples],
            documents=[e["content"] for e in examples],
            metadatas=[{"language": e["language"]} for e in examples],
            embeddings=self._embed([e["content"] for e in examples]),
        )

        logger.info(
            f"Seeded {len(grammar_rules)} grammar rules and {len(examples)} examples"
        )

    def search_grammar(
        self,
        query: str,
        language: Optional[str] = None,
        n_results: int = 3,
    ) -> list[dict]:
        """Search grammar rules.

        Args:
            query: Search query.
            language: Optional language filter.
            n_results: Number of results to return.

        Returns:
            List of matching grammar rules with content and metadata.
        """
        where_filter = None
        if language:
            where_filter = {"$or": [{"language": language}, {"language": "General"}]}

        results = self._grammar_collection.query(
            query_embeddings=self._embed([query]),
            n_results=n_results,
            where=where_filter,
        )

        return self._format_results(results)

    def search_examples(
        self,
        query: str,
        language: Optional[str] = None,
        n_results: int = 3,
    ) -> list[dict]:
        """Search example sentences.

        Args:
            query: Search query.
            language: Optional language filter.
            n_results: Number of results to return.

        Returns:
            List of matching examples.
        """
        where_filter = {"language": language} if language else None

        results = self._examples_collection.query(
            query_embeddings=self._embed([query]),
            n_results=n_results,
            where=where_filter,
        )

        return self._format_results(results)

    def search_all(
        self,
        query: str,
        language: Optional[str] = None,
        n_results: int = 5,
    ) -> list[str]:
        """Search all collections and return combined context.

        Args:
            query: Search query.
            language: Optional language filter.
            n_results: Number of results per collection.

        Returns:
            List of relevant context strings.
        """
        grammar = self.search_grammar(query, language, n_results)
        examples = self.search_examples(query, language, n_results // 2 or 1)

        context = []
        for g in grammar:
            context.append(f"Grammar: {g['content']}")
        for e in examples:
            context.append(f"Example: {e['content']}")

        return context

    def _format_results(self, results: dict) -> list[dict]:
        """Format ChromaDB results into a list of dicts.

        Args:
            results: Raw ChromaDB query results.

        Returns:
            Formatted list of result dicts.
        """
        formatted = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                formatted.append(
                    {
                        "content": doc,
                        "metadata": results["metadatas"][0][i]
                        if results["metadatas"]
                        else {},
                        "id": results["ids"][0][i] if results["ids"] else None,
                    }
                )
        return formatted

    def add_grammar_rule(
        self,
        rule_id: str,
        content: str,
        language: str,
    ):
        """Add a new grammar rule.

        Args:
            rule_id: Unique rule ID.
            content: Rule content/explanation.
            language: Language this rule applies to.
        """
        self._grammar_collection.add(
            ids=[rule_id],
            documents=[content],
            metadatas=[{"language": language}],
            embeddings=self._embed([content]),
        )
        logger.info(f"Added grammar rule: {rule_id}")

    def health_check(self) -> bool:
        """Check if RAG service is healthy.

        Returns:
            True if healthy, False otherwise.
        """
        try:
            # Check ChromaDB
            self._client.heartbeat()

            # Check embedding model
            test_embedding = self._embed(["test"])

            return len(test_embedding) > 0 and len(test_embedding[0]) > 0
        except Exception as e:
            logger.error(f"RAG health check failed: {e}")
            return False


# Cached instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get the RAG service instance.

    Returns:
        RAG service singleton instance.
    """
    global _rag_service

    if _rag_service is None:
        settings = get_settings()
        _rag_service = RAGService(settings)

    return _rag_service
