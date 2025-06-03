--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8
-- Dumped by pg_dump version 16.8

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: attendancestatusenum; Type: TYPE; Schema: public; Owner: scana_user
--

CREATE TYPE public.attendancestatusenum AS ENUM (
    'hadir',
    'tidak_hadir'
);


ALTER TYPE public.attendancestatusenum OWNER TO scana_user;

--
-- Name: roleenum; Type: TYPE; Schema: public; Owner: scana_user
--

CREATE TYPE public.roleenum AS ENUM (
    'admin',
    'user'
);


ALTER TYPE public.roleenum OWNER TO scana_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: scana_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO scana_user;

--
-- Name: attendances; Type: TABLE; Schema: public; Owner: scana_user
--

CREATE TABLE public.attendances (
    id integer NOT NULL,
    meeting_id integer,
    class_student_id integer,
    check_in_time timestamp without time zone,
    check_out_time timestamp without time zone,
    status public.attendancestatusenum
);


ALTER TABLE public.attendances OWNER TO scana_user;

--
-- Name: attendances_id_seq; Type: SEQUENCE; Schema: public; Owner: scana_user
--

CREATE SEQUENCE public.attendances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendances_id_seq OWNER TO scana_user;

--
-- Name: attendances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scana_user
--

ALTER SEQUENCE public.attendances_id_seq OWNED BY public.attendances.id;


--
-- Name: class_students; Type: TABLE; Schema: public; Owner: scana_user
--

CREATE TABLE public.class_students (
    id integer NOT NULL,
    class_id integer,
    student_id integer
);


ALTER TABLE public.class_students OWNER TO scana_user;

--
-- Name: class_students_id_seq; Type: SEQUENCE; Schema: public; Owner: scana_user
--

CREATE SEQUENCE public.class_students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.class_students_id_seq OWNER TO scana_user;

--
-- Name: class_students_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scana_user
--

ALTER SEQUENCE public.class_students_id_seq OWNED BY public.class_students.id;


--
-- Name: classes; Type: TABLE; Schema: public; Owner: scana_user
--

CREATE TABLE public.classes (
    id integer NOT NULL,
    name character varying NOT NULL,
    course_id integer
);


ALTER TABLE public.classes OWNER TO scana_user;

--
-- Name: classes_id_seq; Type: SEQUENCE; Schema: public; Owner: scana_user
--

CREATE SEQUENCE public.classes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.classes_id_seq OWNER TO scana_user;

--
-- Name: classes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scana_user
--

ALTER SEQUENCE public.classes_id_seq OWNED BY public.classes.id;


--
-- Name: courses; Type: TABLE; Schema: public; Owner: scana_user
--

CREATE TABLE public.courses (
    id integer NOT NULL,
    course_id character varying NOT NULL,
    name character varying NOT NULL,
    semester character varying NOT NULL,
    academic_year character varying NOT NULL
);


ALTER TABLE public.courses OWNER TO scana_user;

--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: scana_user
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.courses_id_seq OWNER TO scana_user;

--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scana_user
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- Name: meetings; Type: TABLE; Schema: public; Owner: scana_user
--

CREATE TABLE public.meetings (
    id integer NOT NULL,
    date timestamp without time zone NOT NULL,
    start_time character varying NOT NULL,
    end_time character varying NOT NULL,
    class_id integer
);


ALTER TABLE public.meetings OWNER TO scana_user;

--
-- Name: meetings_id_seq; Type: SEQUENCE; Schema: public; Owner: scana_user
--

CREATE SEQUENCE public.meetings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.meetings_id_seq OWNER TO scana_user;

--
-- Name: meetings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scana_user
--

ALTER SEQUENCE public.meetings_id_seq OWNED BY public.meetings.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: scana_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying NOT NULL,
    password_hash character varying NOT NULL,
    name character varying NOT NULL,
    nim character varying,
    email character varying NOT NULL,
    phone character varying,
    hand_left_path character varying,
    hand_right_path character varying,
    hand_scan_class_index integer,
    role public.roleenum
);


ALTER TABLE public.users OWNER TO scana_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: scana_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO scana_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scana_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: attendances id; Type: DEFAULT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.attendances ALTER COLUMN id SET DEFAULT nextval('public.attendances_id_seq'::regclass);


--
-- Name: class_students id; Type: DEFAULT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.class_students ALTER COLUMN id SET DEFAULT nextval('public.class_students_id_seq'::regclass);


--
-- Name: classes id; Type: DEFAULT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.classes ALTER COLUMN id SET DEFAULT nextval('public.classes_id_seq'::regclass);


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: meetings id; Type: DEFAULT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.meetings ALTER COLUMN id SET DEFAULT nextval('public.meetings_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: scana_user
--

COPY public.alembic_version (version_num) FROM stdin;
365b54bdd1f9
\.


--
-- Data for Name: attendances; Type: TABLE DATA; Schema: public; Owner: scana_user
--

COPY public.attendances (id, meeting_id, class_student_id, check_in_time, check_out_time, status) FROM stdin;
2	18	21	2025-05-18 03:34:16.108568	\N	hadir
3	18	20	2025-05-18 04:11:30.961977	\N	hadir
4	18	24	2025-05-18 04:58:57.846303	\N	hadir
5	19	21	2025-05-18 18:52:43.097198	\N	hadir
6	19	15	2025-05-18 18:53:53.970953	\N	hadir
7	19	29	2025-05-18 19:12:23.63857	\N	hadir
8	19	27	2025-05-18 19:14:09.380428	\N	hadir
9	19	20	2025-05-18 19:16:16.730787	\N	hadir
10	19	4	2025-05-18 19:32:52.555216	\N	hadir
11	19	7	2025-05-18 20:00:17.622823	\N	hadir
12	19	24	2025-05-18 20:02:09.620018	\N	hadir
13	23	28	2025-05-25 10:02:30.928633	\N	hadir
14	23	6	2025-05-25 10:05:05.889101	\N	hadir
15	25	8	2025-05-25 23:05:15.234502	\N	hadir
16	25	4	2025-05-25 23:06:23.113269	2025-05-25 23:06:44.591469	hadir
17	25	27	2025-05-25 23:14:40.556889	2025-05-25 23:15:33.08372	hadir
18	25	21	2025-05-25 23:15:42.303743	\N	hadir
21	26	8	2025-05-26 08:11:13.414127	\N	hadir
19	26	4	2025-05-26 08:10:06.97811	2025-05-26 08:46:04.879461	hadir
22	26	24	2025-05-26 08:11:33.454371	2025-05-26 08:47:38.474584	hadir
23	26	7	2025-05-26 08:32:08.125308	2025-05-26 08:55:26.333581	hadir
25	26	23	2025-05-26 09:02:28.700703	\N	hadir
26	26	30	2025-05-26 09:07:00.312592	\N	hadir
27	26	28	2025-05-26 09:10:17.661285	\N	hadir
30	26	16	2025-05-26 10:35:38.640326	\N	hadir
28	26	6	2025-05-26 09:33:24.210727	2025-05-26 10:37:32.853693	hadir
20	26	27	2025-05-26 08:10:55.20361	2025-05-26 10:38:21.720035	hadir
32	28	37	2025-05-26 11:59:11.281173	\N	hadir
33	28	38	2025-05-26 11:59:49.223624	\N	hadir
34	28	39	2025-05-26 11:59:57.764917	\N	hadir
31	28	36	2025-05-26 11:41:56.455898	2025-05-26 12:01:53.194819	hadir
24	26	5	2025-05-26 08:56:26.522417	2025-05-26 15:35:50.192583	hadir
29	26	20	2025-05-26 10:33:46.141605	2025-05-26 15:37:17.446114	hadir
35	29	40	2025-05-26 15:47:17.388562	\N	hadir
37	30	39	2025-05-31 16:04:40.422597	\N	hadir
38	30	44	2025-05-31 16:09:15.709618	\N	hadir
39	30	46	2025-05-31 16:11:57.059637	\N	hadir
41	30	45	2025-05-31 16:34:22.468913	\N	hadir
40	30	36	2025-05-31 16:19:38.659167	2025-05-31 23:09:05.221671	hadir
36	30	37	2025-05-31 16:03:02.950964	2025-05-31 23:10:31.243418	hadir
43	32	30	2025-06-01 00:35:54.241937	\N	hadir
44	32	24	2025-06-01 00:36:16.442777	\N	hadir
46	32	15	2025-06-01 00:37:18.798502	\N	hadir
47	32	27	2025-06-01 00:37:34.543515	\N	hadir
42	32	4	2025-06-01 00:35:12.873634	2025-06-01 18:22:35.860495	hadir
45	32	20	2025-06-01 00:36:51.363689	2025-06-01 18:23:10.238381	hadir
\.


--
-- Data for Name: class_students; Type: TABLE DATA; Schema: public; Owner: scana_user
--

COPY public.class_students (id, class_id, student_id) FROM stdin;
4	14	22
5	14	24
6	14	26
7	14	28
8	14	30
9	14	5
10	14	6
11	14	7
12	14	8
13	14	9
14	14	10
15	14	11
16	14	12
17	14	13
18	14	14
19	14	15
20	14	16
21	14	17
22	14	31
23	14	18
24	14	19
25	14	20
26	14	21
27	14	23
28	14	25
29	14	27
30	14	29
32	17	6
33	17	7
34	17	8
35	17	5
36	18	22
37	18	28
38	18	23
39	18	29
40	19	24
41	19	16
42	18	6
43	18	18
44	18	19
45	18	26
46	18	16
47	20	26
\.


--
-- Data for Name: classes; Type: TABLE DATA; Schema: public; Owner: scana_user
--

COPY public.classes (id, name, course_id) FROM stdin;
14	PPL - Kelas 1	4
15	PPL - Kelas 2	4
16	PPL - Kelas 3	4
17	PPL - Kelas 4	4
18	Arskom - Kelas 1	5
19	Bahasa indonesia - Kelas 1	6
20	Bahasa indonesia - Kelas 2	6
\.


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: scana_user
--

COPY public.courses (id, course_id, name, semester, academic_year) FROM stdin;
4	INF0000	PPL	ganjil	2025
5	INF98690	Arskom	genap	2025
6	1122	Bahasa indonesia	ganjil	2024/2025
\.


--
-- Data for Name: meetings; Type: TABLE DATA; Schema: public; Owner: scana_user
--

COPY public.meetings (id, date, start_time, end_time, class_id) FROM stdin;
18	2025-05-18 00:00:00	03:14	06:30	14
19	2025-05-18 00:00:00	17:14	20:30	14
20	2025-05-19 00:00:00	10:48	12:56	14
21	2025-05-19 00:00:00	14:10	14:30	14
22	2025-05-24 00:00:00	11:09	12:09	14
23	2025-05-25 00:00:00	09:32	12:32	14
24	2025-05-25 00:00:00	23:01	13:00	17
25	2025-05-25 00:00:00	23:04	23:30	14
26	2025-05-26 00:00:00	08:09	12:09	14
27	2025-05-26 00:00:00	11:03	13:30	17
28	2025-05-26 00:00:00	11:12	13:30	18
29	2025-05-26 00:00:00	15:45	16:45	19
30	2025-05-31 00:00:00	16:02	18:02	18
31	2025-05-31 00:00:00	16:33	07:33	18
32	2025-06-01 00:00:00	00:34	15:50	14
33	2025-06-01 00:00:00	01:34	02:30	20
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: scana_user
--

COPY public.users (id, username, password_hash, name, nim, email, phone, hand_left_path, hand_right_path, hand_scan_class_index, role) FROM stdin;
4	admin	pbkdf2:sha256:1000000$ZWenIf0zxx3Z8wwc$df9621a946ae68a227f6897da2069fdc6856e252e89ee7d95011312370412a09	Admin	\N	admin@example.com	\N	\N	\N	\N	admin
22	22013017	scrypt:32768:8:1$G0avD822C4WQ0sp4$01660ff9564bba19adefa5524f2d6090ffa0af9afa34d776baabc192615c319ae20e2075dcfc95afa51d7c1f67f8716157a801a8e52451b61362d673247a22ff	Janehfers Mandagi	22013017	22013017@unikadelasalle.ac.id	087712345432	storage/hands/22013017/left\\22013017_left_4ce16f03eb1a4239a5f816456d737c71.jpg	storage/hands/22013017/right\\22013017_right_d743ad80abba44f39379c313989adace.jpg	17	user
24	22013020	scrypt:32768:8:1$v7PEQRWOM9ePb0iZ$234f4a570d5c41f6cff1404aee2613a08bf9796c5235dd0597bdea536212e0d2ba87c1a6212e130a3d0fda6039552f220dd8f92b933ab351d9b3d041468b1e0a	Caren Ngantung	22013020	22013020@unikadelasalle.ac.id	083322445678	storage/hands/22013020/left\\22013020_left_8ad8e06c6f1d47418d88bbde86a83ef5.jpg	storage/hands/22013020/right\\22013020_right_512fa22466084b5dabee8aff757e781c.jpg	19	user
26	22013022	scrypt:32768:8:1$uDdZTkqPi57A41Kz$d6b499451becd1af8fc86ab1429ea08fd6d7668db65d99eb20964004c2258ffd5622a4b77ce91f6bb982087efce325876bcede8cf4cddc3f98d9c9510c0c643f	Monica Aprilia Pandeiroth	22013022	22013022@unikadelasalle.ac.id	085233445566	storage/hands/22013022/left\\22013022_left_3720e8cd97a44d17bd9a36f2c8bdffbf.jpg	storage/hands/22013022/right\\22013022_right_3f44481a632a46dd9af9ec63aa1af2df.jpg	21	user
28	22013025	scrypt:32768:8:1$sIHgE9uQ9P7WDDDw$7303991b5f94a4a343a8fcbc446cdda99be44b9306ca4c7c072667c3000aea57e3d444d4f70f79e08b5ee93ed3743755377f9919addbbf06e437aaeb45ea2676	Syalomitha Andries	22013025	22013025@unikadelasalle.ac.id	089977663344	storage/hands/22013025/left\\22013025_left_6b90ffc6b6274ff799f66048dba9472c.jpg	storage/hands/22013025/right\\22013025_right_abbb8aec944b480b88aac5b3cb2132bb.jpg	23	user
30	22013034	scrypt:32768:8:1$gYz0KfRzUqo4bOwU$0ad042ee294f6e668cd242d56baa677415c0fa177a8f914dc40550c8ba87f372d657ec60cb9f6eb323849726b4cf79fdc21142382fd072a52f012e287e257610	Desinta Nayalim	22013034	22013034@unikadelasalle.ac.id	088877332244	storage/hands/22013034/left\\22013034_left_b4309ce644c2418396729faf19ce7e5f.jpg	storage/hands/22013034/right\\22013034_right_1abc0b52345348628273702dfd22d611.jpg	25	user
5	19013049	scrypt:32768:8:1$J7AB4WXVFJ0ffT6D$05d9a5f47b142b73cd7368bb6040b09e96e4db7930cb96d7ffbd1c4f808e74856988834a3efb841de0da15dc1cc8403930b6beccd5baeac83f2fb44c0d2db9dd	Juanita Assa	19013049	19013049@unikadelasalle.ac.id	08123748930	storage/hands/19013049/left\\19013049_left_e56b03449bcc47bdae963df637c5198c.jpg	storage/hands/19013049/right\\19013049_right_6cb0041491474250952f44aa8b6eedcb.jpg	0	user
6	20013017	scrypt:32768:8:1$g2xpS7pV8nhJHab7$935f5a785067f72e84fd0b29a8caa832e03d9d060632ccc5e6de47dd9a7f7028f028f2e0ac413ce8f2ec9f01ac5bacd1a9ce60fc3083b1beb07b4f1acd3405c4	Tetsuo	20013017	20013017@unikadelasalle.ac.id	089533445566	storage/hands/20013017/left\\20013017_left_496bbe97a6194edbba1f94ccd7fc1d95.jpg	storage/hands/20013017/right\\20013017_right_f028357258c74eb7a5f7d1e45668257e.jpg	1	user
7	20013033	scrypt:32768:8:1$LRS27k06BSY90qIe$1cc11d43b83c3fe803e5a0146f8987be7c1f0c4e367a2f907e233d1953c302bb96b64d3eda8f9d52e2351504f5f8a30db96b16b1655d7d80e0e83091e1d3464b	Crosbi	20013033	20013033@unikadelasalle.ac.id	0817263839	storage/hands/20013033/left\\20013033_left_2ab9c7b03c344964af84b9a5aafe1e1e.jpg	storage/hands/20013033/right\\20013033_right_653990217c2c49a7993ad754af26f51a.jpg	2	user
8	20013035	scrypt:32768:8:1$7AkuHgF2mxdlxtgQ$2e3ef6b7c5b3ff9c4a7a7141d30a17fcb91b3393a8fda44de58ac2857d2f6c9c91e9c98d338f7d3669f26513733d7a1c2d10a750489c197b21f0d22e7ed2c332	Innosensius Knaofmone	20013035	20013035@unikadelasalle.ac.id	081212345678	storage/hands/20013035/left\\20013035_left_a069f3b1dfae4e73b5052f68f66e9782.jpg	storage/hands/20013035/right\\20013035_right_b034b79140fb470591c73031a042f998.jpg	3	user
9	20013049	scrypt:32768:8:1$FRYZAaUvYsruWN2y$99676fc5579d4c18b9beb7567b1db343d1a9bec089cabfa8e37d473436a20383ac37a43a424fb6233bd0b7b10cd64484a919d7a413042bc25d753e1289c16d48	Brooklyn Kairupan	20013049	20013049@unikadelasalle.ac.id	083738393931	storage/hands/20013049/left\\20013049_left_2b74c2252df74d4395f5e1cbee266799.jpg	storage/hands/20013049/right\\20013049_right_99cf37d79a6445aa81d87c00f6dfc3ca.jpg	4	user
10	20013055	scrypt:32768:8:1$WeYRjQotudXUmWUH$c0b02d9c80bcf277d3644329bc49aacd0542fc50b817f6b0384db63b24fb2449e38ecf4f876ea37e4ecaea7166d94c86706efb11ebe4a1bb186fb6b874727fc3	Intan Makasaehe	20013055	20013055@unikadelasalle.ac.id	083322451122	storage/hands/20013055/left\\20013055_left_b39ce94b24d644ec83acc7bf400d077d.jpg	storage/hands/20013055/right\\20013055_right_6c92747e96674a49825884f63629507f.jpg	5	user
11	21013004	scrypt:32768:8:1$962u7GbxJ4c9I7DM$09b547462b9dee08f9e3415b9bf19ff95184e8ae63df7a5630804302be2e552049187aa5d9d05dcbc89621714340e334b04952d464730c080f32658046a3441f	Alexanto Supit	21013004	21013004@unikadelasalle.ac.id	0837484338	storage/hands/21013004/left\\21013004_left_e9cf66ce4a9f43b0bb436a98eb134845.jpg	storage/hands/21013004/right\\21013004_right_fb91fbeaa2ea4606943bbdaaaf4547d9.jpg	6	user
12	21013011	scrypt:32768:8:1$ndVX1uEdivz1y8e1$7590a6eb98c62ff12dbf4658709fb46a3c3f09d80db83820c640a315858d48207c0658988a3198720bef78aebbdebf67bc968c245031c3fecb33ff3f40be799c	Jesika Sumampow	21013011	21013011@unikadelasalle.ac.id	081344552233	storage/hands/21013011/left\\21013011_left_e91243fc4b21430b94a10c6339280216.jpg	storage/hands/21013011/right\\21013011_right_14dcba8326a049989ec100d4b80101af.jpg	7	user
13	21013018	scrypt:32768:8:1$eEz02rCqv1WszdJW$59ccb709a20bfc2f55899aa1b957c84a56ca6b575d36cc2218698a2b8b165f722f551a7cbe0ccc61a249ea1f240737eaa5c5fec000567b32dfe56ac6d72da0bd	Axel Dapi	21013018	21013018@unikadelasalle.ac.id	0827374892	storage/hands/21013018/left\\21013018_left_2936a326a53841e394e3f4e694a0bf4e.jpg	storage/hands/21013018/right\\21013018_right_e41d366371d24f5a97f0d5a10042566a.jpg	8	user
14	21013024	scrypt:32768:8:1$6KtwuTiuDpCENNqX$8cf2da2ee7811770410de7f41989ebe381ad9e9cf6269daf3aed69192f7be524ab02e5b0caab6544db94edd023a5bb4170ecb9c38b770472f51ca46822d077e1	Reedante Mirza	21013024	21013024@unikadelasalle.ac.id	089566132245	storage/hands/21013024/left\\21013024_left_51d262a0eae1499b8f8ca3f629d3f9f2.jpg	storage/hands/21013024/right\\21013024_right_9610d23e16c244c7b6281234f8d41d9d.jpg	9	user
15	21013035	scrypt:32768:8:1$1UIppfLRvnaPZal9$bb97accea2da06811c27d7f4a65dd797b1434ad19401a6c411fe404b3b2e42cb95d1928f5117e6e8542d47d6d9c6ae134d4c4a1c4df2a3203fe583ef879747ae	Gratio Paat	21013035	21013035@unikadelasalle.ac.id	08273833378	storage/hands/21013035/left\\21013035_left_195e3c12caea46d9a0411e175c3e04f0.jpg	storage/hands/21013035/right\\21013035_right_04427c12a9c44adaad3c0029a429842a.jpg	10	user
16	22013002	scrypt:32768:8:1$Tc8tYFU7aoqK1DOW$196d88971207490567e776a73f5f40c18f5593fd1a74e0ad1835a282063d0c7f62789b141908dab6286b98180007de8f2491d5db61d57c00b81c7781ebff1d20	Melia Kuntono	22013002	22013002@unikadelasalle.ac.id	0895342505626	storage/hands/22013002/left\\22013002_left_d199fc1b52de47c1983d8e6ba1780aca.jpg	storage/hands/22013002/right\\22013002_right_9b10f27c0fff48db87d3dcd7b64e8dc1.jpg	11	user
17	22013004	scrypt:32768:8:1$mkvFOrXrnJ19GVH1$b454109a9e9ded29ada323b8c632a0f06a007062c5b0825fe63fa9a9c722fd99c1771dff2bac210c23dc520ec5d6e92696d4d319336f523e6643353a87813c15	Andrew Tumewu	22013004	22013004@unikadelasalle.ac.id	083838399173	storage/hands/22013004/left\\22013004_left_98bcddedc1a2454a886b154a79630b4e.jpg	storage/hands/22013004/right\\22013004_right_86f1f1fe4a1b4c41825f2f6995a58941.jpg	12	user
31	22013041	scrypt:32768:8:1$PtLcMuHgUZQ54IIi$3e30a3fed194f5f96e8bdf6acf19688826fe9a2b30ae0eef8170bd502e4dce7375979b67849656600c0ae9b73b58d3d8c0f55eaff04a53a69adb209a7967bd12	Miracle Kalempouw	22013041	22013041@unikadelasalle.ac.id	082833891	storage/hands/22013041/left\\22013041_left_807b675d6059466b986d067faa092de5.jpg	storage/hands/22013041/right\\22013041_right_70b029498f034d9dbd088b9afb6f8a97.jpg	26	user
18	22013006	scrypt:32768:8:1$Mgj368yCX8errKBx$8dd89e119b912566a2fde7667926a212d970deb93e4b4ea81b9906ee04b7cf54870f73fe9dc9bd829ed2e9fa76e793821e8a10660602e3ebdad1d459a8053820	Sesilia Mutiara Pandejlaki	22013006	22013006@unikadelasalle.ac.id	08125825000	storage/hands/22013006/left\\22013006_left_624f09f3d2da4fefa2243915412dcf76.jpg	storage/hands/22013006/right\\22013006_right_2a50d57aa052462295a0e6f00cb38383.jpg	13	user
19	22013008	scrypt:32768:8:1$7gpUd1368mkaeZUp$3b6d408e8f4340706cdabb8fdf3c940dab7da2d541166a2b0cec110b534f5a7b4b1ecdc88420df6b5b242b1e0e95a53f70e463bf77e099361c64056af39a7a9e	Monica Pandejlaki	22013008	22013008@unikadelasalle.ac.id	08373748294	storage/hands/22013008/left\\22013008_left_aacbcdabbfab4188ba6182e4273c1373.jpg	storage/hands/22013008/right\\22013008_right_f237f9822c6b40e6a63e1492f0b34fef.jpg	14	user
20	22013009	scrypt:32768:8:1$jGYIhx8cE3yrniGE$673c553f886b67d98c99101f44e449f650cc8ebfda052ab0a034443f0621faaf7a2fb06d252e04308477277af4ae1a10d3c5d98a3de6a20a85a7f0464df73234	Rafelshen Kakalang	22013009	22013009@unikadelasalle.ac.id	0881277334455	storage/hands/22013009/left\\22013009_left_cb3cf42a91674209a12b50e5a54f3c4b.jpg	storage/hands/22013009/right\\22013009_right_59fae354e9614cfa933e87e573713cf3.jpg	15	user
21	22013011	scrypt:32768:8:1$ycxBeDwe1qDkHOzn$110097e5158a4d946ff1f141c9c2e0b09cc63ad40b7f9ab9a56c6578780da6c0e2d41ad149da1f38fc0016609c26e69aa6bdbc95ba68ba38ab7e44b23c426e90	Edgard Oley	22013011	22013011@unikadelasalle.ac.id	09383739919	storage/hands/22013011/left\\22013011_left_bfb8f79eac8542b6adf5e3134d1d9f56.jpg	storage/hands/22013011/right\\22013011_right_43c5056b79644ebab5292f0078592859.jpg	16	user
23	22013018	scrypt:32768:8:1$M7GvqMqVmdJrvO9U$77d06394fcc4c89b151aa6d03944d3632b5418d37b324b19ca2c66bc67a443c8e1d0b0049015ba62b9b16f284efade55f62be50e87e6923c8f9a8532d6ac723a	Vincensius Wijaya	22013018	22013018@unikadelasalle.ac.id	083748492	storage/hands/22013018/left\\22013018_left_1f53d12fa768421a852b882da4316c8a.jpg	storage/hands/22013018/right\\22013018_right_d6cc7044a98f4e1d869f697de3d3b1b4.jpg	18	user
25	22013021	scrypt:32768:8:1$tddQbhTjzVr9MUgk$cfafc9b50b33b7005856e6023707ad6c4c58e13d3a51b7b6f185e7153e13856d042ce4c3a2eff1c8dc686a8958ac9dd509a8e4e79adc79837632a1f2ee2660a0	Algy Ngenget	22013021	22013021@unikadelasalle.ac.id	082138383992	storage/hands/22013021/left\\22013021_left_fe4513e59eb04c51be807dadb8b38888.jpg	storage/hands/22013021/right\\22013021_right_7e36eae6545447ad89f9dea709ffec51.jpg	20	user
27	22013024	scrypt:32768:8:1$WWV4w616cf4VyFnd$612747a2372fddbb49d3df1e8f171dce4adcac884d1e8dbd5800fad2b5f3b1e41e4a47857c77dc55f67a8a36f5fa18719f0a5e71fecc90d7e7b09d7f4d3f93b5	Vanessa Dipan	22013024	22013024@unikadelasalle.ac.id	092838381	storage/hands/22013024/left\\22013024_left_bdc65aa59bce4b28a7fb7ff97fcae044.jpg	storage/hands/22013024/right\\22013024_right_f9686b2a3c384a1aa083869c6b2b31f5.jpg	22	user
29	22013026	scrypt:32768:8:1$PNqgJiX7zZQ3vDBB$ce6b7c196351c517756ee25976265257906a11160be8721962ff310484a14a1041ae0927f648e0ee379d6d6cb9909ed566169d23894b341ffb55a7a98f899f3a	Hizkia Pinatik	22013026	22013026@unikadelasalle.ac.id	0828389119	storage/hands/22013026/left\\22013026_left_455a7982244b4fc388f574bf7a38e544.jpg	storage/hands/22013026/right\\22013026_right_56187fbd1c7f4349a5bec6ced23075ce.jpg	24	user
32	237820	scrypt:32768:8:1$UYOy32Rr5EIZjpA8$5eccfdbe0c4d59f354436c5ff022e7c339043263c3d5355bea13ab236940182eb3fb6399efddb2fdea99dd4c2d3036458bf59a8311b13ee08cf145766d85ba07	Salsa	237820	Salsa@gmail.com	02828	storage/hands/237820/left\\237820_left_6c75ddf951344eb3bdb8bd7815c38c37.jpg	storage/hands/237820/right\\237820_right_f19e17ab4e4d4131acd32b64ca6a9f28.jpg	\N	user
\.


--
-- Name: attendances_id_seq; Type: SEQUENCE SET; Schema: public; Owner: scana_user
--

SELECT pg_catalog.setval('public.attendances_id_seq', 47, true);


--
-- Name: class_students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: scana_user
--

SELECT pg_catalog.setval('public.class_students_id_seq', 47, true);


--
-- Name: classes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: scana_user
--

SELECT pg_catalog.setval('public.classes_id_seq', 20, true);


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: scana_user
--

SELECT pg_catalog.setval('public.courses_id_seq', 6, true);


--
-- Name: meetings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: scana_user
--

SELECT pg_catalog.setval('public.meetings_id_seq', 33, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: scana_user
--

SELECT pg_catalog.setval('public.users_id_seq', 32, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: attendances attendances_pkey; Type: CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.attendances
    ADD CONSTRAINT attendances_pkey PRIMARY KEY (id);


--
-- Name: class_students class_students_pkey; Type: CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.class_students
    ADD CONSTRAINT class_students_pkey PRIMARY KEY (id);


--
-- Name: classes classes_pkey; Type: CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_pkey PRIMARY KEY (id);


--
-- Name: courses courses_course_id_key; Type: CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_course_id_key UNIQUE (course_id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: meetings meetings_pkey; Type: CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.meetings
    ADD CONSTRAINT meetings_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_hand_scan_class_index_key; Type: CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_hand_scan_class_index_key UNIQUE (hand_scan_class_index);


--
-- Name: users users_nim_key; Type: CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_nim_key UNIQUE (nim);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: ix_attendances_id; Type: INDEX; Schema: public; Owner: scana_user
--

CREATE INDEX ix_attendances_id ON public.attendances USING btree (id);


--
-- Name: ix_class_students_id; Type: INDEX; Schema: public; Owner: scana_user
--

CREATE INDEX ix_class_students_id ON public.class_students USING btree (id);


--
-- Name: ix_classes_id; Type: INDEX; Schema: public; Owner: scana_user
--

CREATE INDEX ix_classes_id ON public.classes USING btree (id);


--
-- Name: ix_courses_id; Type: INDEX; Schema: public; Owner: scana_user
--

CREATE INDEX ix_courses_id ON public.courses USING btree (id);


--
-- Name: ix_meetings_id; Type: INDEX; Schema: public; Owner: scana_user
--

CREATE INDEX ix_meetings_id ON public.meetings USING btree (id);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: scana_user
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: attendances attendances_class_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.attendances
    ADD CONSTRAINT attendances_class_student_id_fkey FOREIGN KEY (class_student_id) REFERENCES public.class_students(id);


--
-- Name: attendances attendances_meeting_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.attendances
    ADD CONSTRAINT attendances_meeting_id_fkey FOREIGN KEY (meeting_id) REFERENCES public.meetings(id);


--
-- Name: class_students class_students_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.class_students
    ADD CONSTRAINT class_students_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id);


--
-- Name: class_students class_students_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.class_students
    ADD CONSTRAINT class_students_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.users(id);


--
-- Name: classes classes_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id);


--
-- Name: meetings meetings_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: scana_user
--

ALTER TABLE ONLY public.meetings
    ADD CONSTRAINT meetings_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id);


--
-- PostgreSQL database dump complete
--

