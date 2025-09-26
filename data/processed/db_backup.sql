--
-- PostgreSQL database dump
--

\restrict Ha57yTEqbL1zDTSkq9PUT5xiuBcJzQtnur26mncY71y8Pg2XAtvOckzZlnc9XKE

-- Dumped from database version 15.14
-- Dumped by pg_dump version 15.14

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
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: myuser
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO myuser;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: price_snapshots; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.price_snapshots (
    id integer NOT NULL,
    laptop_id integer NOT NULL,
    price numeric(10,2),
    currency character varying(3) DEFAULT 'USD'::character varying,
    availability_status character varying(50),
    shipping_info text,
    promotion_text text,
    configuration_summary text,
    scraped_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.price_snapshots OWNER TO myuser;

--
-- Name: laptop_latest_prices; Type: VIEW; Schema: public; Owner: myuser
--

CREATE VIEW public.laptop_latest_prices AS
 SELECT DISTINCT ON (price_snapshots.laptop_id) price_snapshots.laptop_id,
    price_snapshots.price,
    price_snapshots.currency,
    price_snapshots.availability_status,
    price_snapshots.promotion_text,
    price_snapshots.configuration_summary,
    price_snapshots.scraped_at
   FROM public.price_snapshots
  ORDER BY price_snapshots.laptop_id, price_snapshots.scraped_at DESC;


ALTER TABLE public.laptop_latest_prices OWNER TO myuser;

--
-- Name: reviews; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.reviews (
    id integer NOT NULL,
    laptop_id integer NOT NULL,
    rating integer,
    review_title text,
    review_text text,
    reviewer_name character varying(200),
    reviewer_verified boolean DEFAULT false,
    review_date date,
    helpful_count integer DEFAULT 0,
    configuration_summary text,
    scraped_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT reviews_rating_check CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE public.reviews OWNER TO myuser;

--
-- Name: laptop_review_summary; Type: VIEW; Schema: public; Owner: myuser
--

CREATE VIEW public.laptop_review_summary AS
 SELECT reviews.laptop_id,
    count(*) AS total_reviews,
    (avg(reviews.rating))::numeric(3,2) AS average_rating,
    count(
        CASE
            WHEN (reviews.rating = 5) THEN 1
            ELSE NULL::integer
        END) AS five_star_count,
    count(
        CASE
            WHEN (reviews.rating = 1) THEN 1
            ELSE NULL::integer
        END) AS one_star_count
   FROM public.reviews
  GROUP BY reviews.laptop_id;


ALTER TABLE public.laptop_review_summary OWNER TO myuser;

--
-- Name: laptops; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.laptops (
    id integer NOT NULL,
    brand character varying(50) NOT NULL,
    model_name character varying(200) NOT NULL,
    variant character varying(100),
    full_model_name character varying(300) NOT NULL,
    product_page_url text,
    pdf_spec_url text NOT NULL,
    image_url text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.laptops OWNER TO myuser;

--
-- Name: laptops_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.laptops_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.laptops_id_seq OWNER TO myuser;

--
-- Name: laptops_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.laptops_id_seq OWNED BY public.laptops.id;


--
-- Name: price_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.price_snapshots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.price_snapshots_id_seq OWNER TO myuser;

--
-- Name: price_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.price_snapshots_id_seq OWNED BY public.price_snapshots.id;


--
-- Name: questions_answers; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.questions_answers (
    id integer NOT NULL,
    laptop_id integer NOT NULL,
    question_text text NOT NULL,
    answer_text text,
    asker_name character varying(200),
    answerer_name character varying(200),
    question_date date,
    answer_date date,
    helpful_count integer DEFAULT 0,
    configuration_summary text,
    scraped_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.questions_answers OWNER TO myuser;

--
-- Name: questions_answers_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.questions_answers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.questions_answers_id_seq OWNER TO myuser;

--
-- Name: questions_answers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.questions_answers_id_seq OWNED BY public.questions_answers.id;


--
-- Name: reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reviews_id_seq OWNER TO myuser;

--
-- Name: reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.reviews_id_seq OWNED BY public.reviews.id;


--
-- Name: specifications; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.specifications (
    id integer NOT NULL,
    laptop_id integer NOT NULL,
    category character varying(100) NOT NULL,
    specification_name character varying(200) NOT NULL,
    specification_value text NOT NULL,
    unit character varying(20),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    structured_value jsonb
);


ALTER TABLE public.specifications OWNER TO myuser;

--
-- Name: specifications_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.specifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.specifications_id_seq OWNER TO myuser;

--
-- Name: specifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.specifications_id_seq OWNED BY public.specifications.id;


--
-- Name: laptops id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.laptops ALTER COLUMN id SET DEFAULT nextval('public.laptops_id_seq'::regclass);


--
-- Name: price_snapshots id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.price_snapshots ALTER COLUMN id SET DEFAULT nextval('public.price_snapshots_id_seq'::regclass);


--
-- Name: questions_answers id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.questions_answers ALTER COLUMN id SET DEFAULT nextval('public.questions_answers_id_seq'::regclass);


--
-- Name: reviews id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.reviews ALTER COLUMN id SET DEFAULT nextval('public.reviews_id_seq'::regclass);


--
-- Name: specifications id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.specifications ALTER COLUMN id SET DEFAULT nextval('public.specifications_id_seq'::regclass);


--
-- Data for Name: laptops; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.laptops (id, brand, model_name, variant, full_model_name, product_page_url, pdf_spec_url, image_url, created_at, updated_at) FROM stdin;
1	Lenovo	ThinkPad E14 Gen 5	Intel	ThinkPad E14 Gen 5 (Intel)	https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpade/thinkpad-e14-gen-5-14-inch-intel/len101t0064	https://psref.lenovo.com/syspool/Sys/PDF/ThinkPad/ThinkPad_E14_Gen_5_Intel/ThinkPad_E14_Gen_5_Intel_Spec.PDF	https://p3-ofp.static.pub/fes/cms/2023/05/15/h5cqimqsg3i95ffichjsp8qz9wun5h434750.jpg	2025-09-25 20:35:01.301369+00	2025-09-25 20:35:01.301369+00
2	Lenovo	ThinkPad E14 Gen 5	AMD	ThinkPad E14 Gen 5 (AMD)	https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpade/thinkpad-e14-gen-5-14-inch-amd/len101t0068?orgRef=https%253A%252F%252Fwww.google.com%252F&srsltid=AfmBOoqAS4HFde0cPIpvn4VZodEMsRkvV0akOcfFq_K6PXjuPX2CXlMV	https://psref.lenovo.com/syspool/Sys/PDF/ThinkPad/ThinkPad_E14_Gen_5_AMD/ThinkPad_E14_Gen_5_AMD_Spec.pdf	https://p1-ofp.static.pub/fes/cms/2023/05/30/t7l1v4d7clb4flto8dyzrltuhnyx6y985674.jpg	2025-09-25 20:35:01.301369+00	2025-09-25 20:35:01.301369+00
3	HP	ProBook 450	G10	HP ProBook 450 G10	https://www.hp.com/us-en/shop/pdp/hp-probook-450-156-inch-g10-notebook-pc-wolf-pro-security-edition-p-8l0e0ua-aba-1	https://h20195.www2.hp.com/v2/GetPDF.aspx/c08504822.pdf	https://hp.widen.net/content/wvqwdaw4fy/jpeg/wvqwdaw4fy.jpg?w=1500&dpi=300	2025-09-25 20:35:01.301369+00	2025-09-25 20:35:01.301369+00
4	HP	ProBook 440	G11	HP ProBook 440 G11	https://www.hp.com/us-en/shop/mdp/pro-352502--1/probook-440	https://h20195.www2.hp.com/v2/getpdf.aspx/c08947328.pdf	https://www.hp.com/wcsstore/hpusstore/Treatment/mdps/Q2FY23_Probook_Series_G10_Redesign/Commercial.jpg	2025-09-25 20:35:01.301369+00	2025-09-25 20:35:01.301369+00
\.


--
-- Data for Name: price_snapshots; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.price_snapshots (id, laptop_id, price, currency, availability_status, shipping_info, promotion_text, configuration_summary, scraped_at) FROM stdin;
127	4	724.22	USD	Out of Stock	\N	\N	\N	2025-08-27 15:50:22.831742+00
128	4	747.97	USD	In Stock	\N	\N	\N	2025-08-28 15:50:22.83187+00
129	4	752.58	USD	In Stock	\N	\N	\N	2025-08-29 15:50:22.831901+00
130	4	753.14	USD	In Stock	\N	\N	\N	2025-08-30 15:50:22.831922+00
131	4	709.81	USD	In Stock	\N	\N	\N	2025-08-31 15:50:22.831938+00
132	4	764.94	USD	Limited Stock	\N	\N	\N	2025-09-01 15:50:22.831954+00
133	4	769.62	USD	In Stock	\N	\N	\N	2025-09-02 15:50:22.831968+00
134	4	734.45	USD	In Stock	\N	\N	\N	2025-09-03 15:50:22.83198+00
135	4	766.10	USD	In Stock	\N	\N	\N	2025-09-04 15:50:22.831993+00
136	4	789.15	USD	In Stock	\N	\N	\N	2025-09-05 15:50:22.832005+00
137	4	780.93	USD	Out of Stock	\N	\N	\N	2025-09-06 15:50:22.832016+00
138	4	738.64	USD	In Stock	\N	\N	\N	2025-09-07 15:50:22.832028+00
139	4	789.59	USD	In Stock	\N	\N	\N	2025-09-08 15:50:22.832041+00
140	4	711.61	USD	In Stock	\N	\N	\N	2025-09-09 15:50:22.832056+00
141	4	737.78	USD	Limited Stock	\N	\N	\N	2025-09-10 15:50:22.832067+00
142	4	770.64	USD	In Stock	\N	\N	\N	2025-09-11 15:50:22.832078+00
143	4	754.67	USD	In Stock	\N	\N	\N	2025-09-12 15:50:22.832089+00
144	4	782.60	USD	In Stock	\N	\N	\N	2025-09-13 15:50:22.832101+00
145	4	762.10	USD	In Stock	\N	\N	\N	2025-09-14 15:50:22.832112+00
146	4	798.82	USD	In Stock	\N	\N	\N	2025-09-15 15:50:22.832123+00
147	4	718.50	USD	In Stock	\N	\N	\N	2025-09-16 15:50:22.832133+00
148	4	765.61	USD	Out of Stock	\N	\N	\N	2025-09-17 15:50:22.832144+00
149	4	758.04	USD	In Stock	\N	\N	\N	2025-09-18 15:50:22.832156+00
150	4	780.21	USD	In Stock	\N	\N	\N	2025-09-19 15:50:22.832177+00
151	4	737.68	USD	Limited Stock	\N	\N	\N	2025-09-20 15:50:22.8322+00
152	4	760.99	USD	Out of Stock	\N	\N	\N	2025-09-21 15:50:22.832213+00
153	4	794.10	USD	Out of Stock	\N	\N	\N	2025-09-22 15:50:22.832224+00
154	4	715.93	USD	In Stock	\N	\N	\N	2025-09-23 15:50:22.832237+00
155	4	704.64	USD	In Stock	\N	\N	\N	2025-09-24 15:50:22.832248+00
156	4	792.45	USD	In Stock	\N	\N	\N	2025-09-25 15:50:22.83226+00
157	3	946.10	USD	In Stock	\N	\N	\N	2025-08-27 15:50:22.833323+00
158	3	934.76	USD	In Stock	\N	\N	\N	2025-08-28 15:50:22.83339+00
159	3	900.74	USD	Out of Stock	\N	\N	\N	2025-08-29 15:50:22.83342+00
160	3	926.29	USD	In Stock	\N	\N	\N	2025-08-30 15:50:22.833441+00
161	3	891.39	USD	In Stock	\N	\N	\N	2025-08-31 15:50:22.83346+00
162	3	912.52	USD	In Stock	\N	\N	\N	2025-09-01 15:50:22.833478+00
163	3	892.16	USD	Limited Stock	\N	\N	\N	2025-09-02 15:50:22.833502+00
164	3	881.97	USD	In Stock	\N	\N	\N	2025-09-03 15:50:22.83352+00
165	3	859.33	USD	In Stock	\N	\N	\N	2025-09-04 15:50:22.833538+00
166	3	930.33	USD	In Stock	\N	\N	\N	2025-09-05 15:50:22.833555+00
167	3	859.66	USD	Out of Stock	\N	\N	\N	2025-09-06 15:50:22.833572+00
168	3	866.45	USD	In Stock	\N	\N	\N	2025-09-07 15:50:22.833588+00
169	3	851.65	USD	In Stock	\N	\N	\N	2025-09-08 15:50:22.833606+00
170	3	868.67	USD	In Stock	\N	\N	\N	2025-09-09 15:50:22.833625+00
171	3	882.59	USD	Out of Stock	\N	\N	\N	2025-09-10 15:50:22.833641+00
172	3	907.83	USD	Out of Stock	\N	\N	\N	2025-09-11 15:50:22.833657+00
173	3	944.03	USD	In Stock	\N	\N	\N	2025-09-12 15:50:22.833674+00
174	3	884.97	USD	In Stock	\N	\N	\N	2025-09-13 15:50:22.833693+00
175	3	944.41	USD	In Stock	\N	\N	\N	2025-09-14 15:50:22.833709+00
176	3	882.30	USD	In Stock	\N	\N	\N	2025-09-15 15:50:22.833725+00
177	3	871.06	USD	In Stock	\N	\N	\N	2025-09-16 15:50:22.833741+00
178	3	944.20	USD	Limited Stock	\N	\N	\N	2025-09-17 15:50:22.833764+00
179	3	868.59	USD	In Stock	\N	\N	\N	2025-09-18 15:50:22.833781+00
180	3	903.57	USD	Limited Stock	\N	\N	\N	2025-09-19 15:50:22.833798+00
181	3	896.34	USD	In Stock	\N	\N	\N	2025-09-20 15:50:22.833813+00
182	3	880.97	USD	Out of Stock	\N	\N	\N	2025-09-21 15:50:22.833837+00
183	3	854.31	USD	In Stock	\N	\N	\N	2025-09-22 15:50:22.833856+00
184	3	912.70	USD	Limited Stock	\N	\N	\N	2025-09-23 15:50:22.833873+00
185	3	881.05	USD	In Stock	\N	\N	\N	2025-09-24 15:50:22.833892+00
186	3	928.70	USD	In Stock	\N	\N	\N	2025-09-25 15:50:22.833912+00
187	2	1000.00	USD	In Stock	\N	\N	\N	2025-09-26 15:52:23.834895+00
188	1	1019.00	USD	In Stock	\N	\N	\N	2025-09-26 15:54:30.227379+00
\.


--
-- Data for Name: questions_answers; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.questions_answers (id, laptop_id, question_text, answer_text, asker_name, answerer_name, question_date, answer_date, helpful_count, configuration_summary, scraped_at) FROM stdin;
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.reviews (id, laptop_id, rating, review_title, review_text, reviewer_name, reviewer_verified, review_date, helpful_count, configuration_summary, scraped_at) FROM stdin;
77	4	5	\N	Deployed these across our organization. Great reliability, security features work well, and the price point is competitive for business use.	ITManager_Sarah	f	2025-06-16	0	\N	2025-09-26 10:20:22.827844+00
78	4	4	\N	Runs Excel, QuickBooks, and other accounting software without issues. Good keyboard for data entry. Reliable for daily financial work.	AccountantPro	f	2025-07-11	0	\N	2025-09-26 10:20:22.827844+00
79	4	4	\N	Solid business laptop. The build quality is excellent and performance handles all my office tasks smoothly. Battery life gets me through a full workday.	BusinessUser2024	f	2025-05-25	0	\N	2025-09-26 10:20:22.827844+00
80	4	5	\N	Perfect travel companion. Lightweight enough for constant travel, battery lasts through client meetings, and it's professional looking.	ConsultantLife	f	2025-08-14	0	\N	2025-09-26 10:20:22.827844+00
81	4	3	\N	Does what it needs to do. Not fancy but functional. Good for Microsoft Office suite and web-based project management tools.	ProjectManager_Mike	f	2025-08-11	0	\N	2025-09-26 10:20:22.827844+00
82	4	4	\N	Good for remote work setup. Screen quality is decent, keyboard is comfortable for long typing sessions. Webcam quality could be better.	RemoteWorker	f	2025-09-15	0	\N	2025-09-26 10:20:22.827844+00
83	4	3	\N	Decent performance for the price range. Not the fastest but gets the job done. Would recommend for basic business tasks.	TechReviewer	f	2025-08-29	0	\N	2025-09-26 10:20:22.827844+00
84	3	3	\N	Does what it needs to do. Not fancy but functional. Good for Microsoft Office suite and web-based project management tools.	ProjectManager_Mike	f	2025-07-25	0	\N	2025-09-26 10:20:22.827844+00
85	3	4	\N	Good for remote work setup. Screen quality is decent, keyboard is comfortable for long typing sessions. Webcam quality could be better.	RemoteWorker	f	2025-07-13	0	\N	2025-09-26 10:20:22.827844+00
86	3	4	\N	Solid business laptop. The build quality is excellent and performance handles all my office tasks smoothly. Battery life gets me through a full workday.	BusinessUser2024	f	2025-08-11	0	\N	2025-09-26 10:20:22.827844+00
87	3	4	\N	Runs Excel, QuickBooks, and other accounting software without issues. Good keyboard for data entry. Reliable for daily financial work.	AccountantPro	f	2025-05-26	0	\N	2025-09-26 10:20:22.827844+00
88	3	5	\N	Deployed these across our organization. Great reliability, security features work well, and the price point is competitive for business use.	ITManager_Sarah	f	2025-04-13	0	\N	2025-09-26 10:20:22.827844+00
89	2	4	\N	The laptop is easy to use, compact and the Apps, programs and software all run smoothly.	ReviewUser1	f	2025-08-21	0	\N	2025-09-26 10:22:10.109668+00
90	2	3	\N	keyboard is responsive and the backlit function is useful.	ReviewUser2	f	2025-06-18	0	\N	2025-09-26 10:22:10.109668+00
91	1	5	\N	the laptop was expected to have backlight keyboard (based on sales confirmation before placing the order) but it didn't.	ReviewUser1	f	2025-04-28	0	\N	2025-09-26 10:24:22.275522+00
92	1	4	\N	The laptop is used in an office environment.	ReviewUser2	f	2025-07-21	0	\N	2025-09-26 10:24:22.275522+00
93	1	5	\N	I can do my work with the convenient trackpad and touchscreen.	ReviewUser3	f	2025-04-25	0	\N	2025-09-26 10:24:22.275522+00
94	1	3	\N	This laptop was purchased for the new boss.	ReviewUser4	f	2025-08-30	0	\N	2025-09-26 10:24:22.275522+00
95	1	3	\N	This computer is fast, a good size, great for all my work databases.	ReviewUser5	f	2025-07-05	0	\N	2025-09-26 10:24:22.275522+00
96	1	5	\N	I can multitask and do all my work without any issue because of the speed.	ReviewUser6	f	2025-07-25	0	\N	2025-09-26 10:24:22.275522+00
97	1	4	\N	The laptop works well and provides the functions I need.	ReviewUser7	f	2025-06-25	0	\N	2025-09-26 10:24:22.275522+00
98	1	5	\N	I was again impressed with the quality and function of this laptop.	ReviewUser8	f	2025-06-20	0	\N	2025-09-26 10:24:22.275522+00
99	1	4	\N	The laptop is great, love the configuration and design.	ReviewUser9	f	2025-09-21	0	\N	2025-09-26 10:24:22.275522+00
100	1	3	\N	Great laptop built for work/educational use.	ReviewUser10	f	2025-05-05	0	\N	2025-09-26 10:24:22.275522+00
101	1	4	\N	amazing laptop and I highly recommend.	ReviewUser11	f	2025-05-03	0	\N	2025-09-26 10:24:22.275522+00
102	1	5	\N	Good laptop overall, Easy to set up.	ReviewUser12	f	2025-05-07	0	\N	2025-09-26 10:24:22.275522+00
103	1	5	\N	Great Laptop with awesome configurations.	ReviewUser13	f	2025-04-02	0	\N	2025-09-26 10:24:22.275522+00
104	1	4	\N	keyboard is excellent, and the build quality feels sturdy.	ReviewUser14	f	2025-04-03	0	\N	2025-09-26 10:24:22.275522+00
105	1	5	\N	build quality is premium, and its performance is excellent for my office work.	ReviewUser15	f	2025-07-28	0	\N	2025-09-26 10:24:22.275522+00
\.


--
-- Data for Name: specifications; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.specifications (id, laptop_id, category, specification_name, specification_value, unit, created_at, structured_value) FROM stdin;
1	1	Processor	Core i3 / i5 / i7 Processor - Cores	2	\N	2025-09-25 20:35:02.976136+00	\N
2	1	Processor	Core i3 / i5 / i7 Processor - Cache	10MB	\N	2025-09-25 20:35:02.976136+00	\N
129	4	Connectivity	Ports and Connectors	2 USB Type-C® 20Gbps signaling rate (USB Power Delivery, DisplayPort™ 1.4, HP Sleep and Charge); 2 USB Type-A 5Gbps signaling rate (1 charging, 1 power); 1 HDMI 2.1; 1 stereo headphone/microphone combo jack; 1 RJ-45 ; (HDMI cable sold separately.)	\N	2025-09-25 20:35:03.213623+00	{"ports": ["2 USB Type-C 20Gbps signaling rate (USB Power Delivery, DisplayPort 1.4, HP Sleep and Charge)", "2 USB Type-A 5Gbps signaling rate (1 charging, 1 power)", "1 HDMI 2.1", "1 stereo headphone/microphone combo jack", "1 RJ-45"], "ethernet": true, "wireless_wan": false, "wifi_standard": null, "bluetooth_version": null}
4	1	Processor	Core i3-1315U - Cores	2	\N	2025-09-25 20:35:02.976136+00	\N
5	1	Processor	Core i3-1315U - Cache	10MB	\N	2025-09-25 20:35:02.976136+00	\N
130	4	Connectivity	Communications	(Compatible with Miracast-certified devices.); ; Intel® Wi-Fi 6E AX211 (2x2) and Bluetooth® 5.3 wireless card; Realtek Wi-Fi 6E RTL8852CE 802.11a/b/g/n/ax (2x2) and Bluetooth® 5.3 wireless card ; Qualcomm® 9205 LTE Cat-M1; HP 4000 4G LTE Advanced Pro	\N	2025-09-25 20:35:03.213623+00	{"ports": [], "ethernet": false, "wireless_wan": true, "wifi_standard": "Wi-Fi 6E", "bluetooth_version": "5.3"}
7	1	Processor	Core i5-1335U 10 - Cores	2	\N	2025-09-25 20:35:02.976136+00	\N
8	1	Processor	Core i5-1335U 10 - Cache	12MB	\N	2025-09-25 20:35:02.976136+00	\N
10	1	Processor	Core i5-1340P 12 - Cores	4	\N	2025-09-25 20:35:02.976136+00	\N
11	1	Processor	Core i5-1340P 12 - Cache	12MB	\N	2025-09-25 20:35:02.976136+00	\N
13	1	Processor	Core i513420H - Cores	4	\N	2025-09-25 20:35:02.976136+00	\N
14	1	Processor	Core i513420H - Cache	12MB	\N	2025-09-25 20:35:02.976136+00	\N
16	1	Processor	Core i5-1345U 10 - Cores	2	\N	2025-09-25 20:35:02.976136+00	\N
17	1	Processor	Core i5-1345U 10 - Cache	12MB	\N	2025-09-25 20:35:02.976136+00	\N
19	1	Processor	Core i513500H - Cores	4	\N	2025-09-25 20:35:02.976136+00	\N
20	1	Processor	Core i513500H - Cache	18MB	\N	2025-09-25 20:35:02.976136+00	\N
22	1	Processor	Core i7-1355U 10 - Cores	2	\N	2025-09-25 20:35:02.976136+00	\N
23	1	Processor	Core i7-1355U 10 - Cache	12MB	\N	2025-09-25 20:35:02.976136+00	\N
25	1	Processor	Core i7-1360P 12 - Cores	4	\N	2025-09-25 20:35:02.976136+00	\N
26	1	Processor	Core i7-1360P 12 - Cache	18MB	\N	2025-09-25 20:35:02.976136+00	\N
28	1	Processor	Core i7-1365U 10 - Cores	2	\N	2025-09-25 20:35:02.976136+00	\N
29	1	Processor	Core i7-1365U 10 - Cache	12MB	\N	2025-09-25 20:35:02.976136+00	\N
32	1	Processor	Core i713700H - Cores	6	\N	2025-09-25 20:35:02.976136+00	\N
33	1	Processor	Core i713700H - Cache	24MB	\N	2025-09-25 20:35:02.976136+00	\N
36	1	Memory	Maximum Memory	40GB	\N	2025-09-25 20:35:02.976136+00	\N
71	2	Memory	Maximum Memory	40GB	\N	2025-09-25 20:35:03.049447+00	\N
21	1	Processor	Core i513500H - Frequencies	2.6GHz / E-core 1.9	\N	2025-09-25 20:35:02.976136+00	{"brand": "Intel", "cores": null, "model": "Core i5 13500H", "threads": null, "cache_mb": null, "max_frequency_ghz": 2.6, "base_frequency_ghz": 1.9, "integrated_graphics": null}
24	1	Processor	Core i7-1355U 10 - Frequencies	1.7GHz / E-core 1.2	\N	2025-09-25 20:35:02.976136+00	{"brand": "Intel", "cores": 10, "model": "Core i7-1355U", "threads": null, "cache_mb": null, "max_frequency_ghz": 1.7, "base_frequency_ghz": 1.2, "integrated_graphics": null}
41	1	Physical	Weight	1.43 kg (3.15 lbs)	\N	2025-09-25 20:35:02.976136+00	{"weight_kg": 1.43, "weight_lbs": 3.15, "dimensions_mm": null, "dimensions_inches": null}
42	1	Battery	Battery Option	47Wh Li-ion with Rapid Charge	\N	2025-09-25 20:35:02.976136+00	{"cells": null, "chemistry": "Li-ion", "capacity_wh": 47, "rapid_charge": true, "test_results": [], "battery_life_hours": null}
43	1	Battery	Battery Option	57Wh Li-ion with Rapid Charge	\N	2025-09-25 20:35:02.976136+00	{"cells": null, "chemistry": "Li-ion", "capacity_wh": 57, "rapid_charge": true, "test_results": [], "battery_life_hours": null}
44	1	Battery	Battery Life - MobileMark® 2018	11.2 hours	\N	2025-09-25 20:35:02.976136+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [{"hours": 11.2, "test_name": "MobileMark 2018"}], "battery_life_hours": null}
61	2	Graphics	AMD Ryzen™ 5 5625U 6 - Integrated Graphics	AMD Radeon™ Graphics	\N	2025-09-25 20:35:03.049447+00	{"type": "Integrated", "brand": "AMD", "model": "AMD Radeon™ Graphics", "memory_gb": null}
62	2	Processor	AMD Ryzen™ 5 7430U 6 - Cache	3MB L2	\N	2025-09-25 20:35:03.049447+00	{"brand": "AMD", "cores": null, "model": "AMD Ryzen™ 5 7430U", "threads": null, "cache_mb": 3, "max_frequency_ghz": null, "base_frequency_ghz": null, "integrated_graphics": null}
63	2	Processor	AMD Ryzen™ 5 7430U 6 - Frequencies	2.3GHz 4.3	\N	2025-09-25 20:35:03.049447+00	{"brand": "AMD", "cores": 6, "model": "AMD Ryzen™ 5 7430U", "threads": null, "cache_mb": null, "max_frequency_ghz": 4.3, "base_frequency_ghz": 2.3, "integrated_graphics": null}
64	2	Graphics	AMD Ryzen™ 5 7430U 6 - Integrated Graphics	AMD Radeon™ Graphics	\N	2025-09-25 20:35:03.049447+00	{"type": "Integrated", "brand": "AMD", "model": "AMD Radeon™ Graphics", "memory_gb": null}
65	2	Processor	AMD Ryzen™ 5 7530U 6 - Cache	3MB L2	\N	2025-09-25 20:35:03.049447+00	{"brand": "AMD", "cores": null, "model": "AMD Ryzen™ 5 7530U", "threads": null, "cache_mb": 3, "max_frequency_ghz": null, "base_frequency_ghz": null, "integrated_graphics": null}
66	2	Processor	AMD Ryzen™ 5 7530U 6 - Frequencies	2.0GHz 4.5	\N	2025-09-25 20:35:03.049447+00	{"brand": "AMD", "cores": 6, "model": "AMD Ryzen™ 5 7530U", "threads": null, "cache_mb": null, "max_frequency_ghz": 4.5, "base_frequency_ghz": 2.0, "integrated_graphics": null}
67	2	Graphics	AMD Ryzen™ 5 7530U 6 - Integrated Graphics	AMD Radeon™ Graphics	\N	2025-09-25 20:35:03.049447+00	{"type": "Integrated", "brand": "AMD", "model": "AMD Radeon™ Graphics", "memory_gb": null}
68	2	Processor	AMD Ryzen™ 7 7730U 8 - Cache	4MB L2	\N	2025-09-25 20:35:03.049447+00	{"brand": "AMD", "cores": 8, "model": "AMD Ryzen™ 7 7730U", "threads": null, "cache_mb": 4, "max_frequency_ghz": null, "base_frequency_ghz": null, "integrated_graphics": null}
81	2	Battery	Battery Life - JEITA 2.0	17.34 hours	\N	2025-09-25 20:35:03.049447+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 17.34}
82	2	Battery	Battery Life - MobileMark® 2018	12.38 hours	\N	2025-09-25 20:35:03.049447+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 12.38}
83	2	Battery	Battery Life - JEITA 2.0	14.37 hours	\N	2025-09-25 20:35:03.049447+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 14.37}
121	4	Display	Display Option 2	14" diagonal, WUXGA (1920 x 1200), IPS, anti-glare, 300 nits, 45% NTSC	\N	2025-09-25 20:35:03.213623+00	{"displays": [{"panel_type": "IPS", "resolution": "1920x1200", "color_space": "NTSC", "aspect_ratio": "16:10", "is_touchscreen": false, "brightness_nits": 300, "refresh_rate_hz": 60, "color_gamut_percent": 45, "diagonal_size_inches": 14}], "refresh_rate_hz": 60}
122	4	Display	Display Option 3	14" diagonal, WUXGA (1920 x 1200), touch, IPS, anti-glare, 300 nits, 45% NTSC	\N	2025-09-25 20:35:03.213623+00	{"displays": [{"panel_type": "IPS", "resolution": "1920x1200", "color_space": "NTSC", "aspect_ratio": "16:10", "is_touchscreen": true, "brightness_nits": 300, "refresh_rate_hz": 60, "color_gamut_percent": 45, "diagonal_size_inches": 14}], "refresh_rate_hz": 60}
123	4	Display	Display Option 4	14" diagonal, WQXGA (2560 x 1600), IPS, anti-glare, 500 nits, 100% DCI-P3 35.6 cm (14") diagonal, WUXGA (1920 x 1200), IPS, anti-glare, 400 nits, low power, 100% sRGB with HP Eye Ease	\N	2025-09-25 20:35:03.213623+00	{"displays": [{"panel_type": "IPS", "resolution": "2560x1600", "color_space": "DCI-P3", "aspect_ratio": "16:10", "is_touchscreen": false, "brightness_nits": 500, "refresh_rate_hz": 60, "color_gamut_percent": 100, "diagonal_size_inches": 14}, {"panel_type": "IPS", "resolution": "1920x1200", "color_space": "sRGB", "aspect_ratio": "16:10", "is_touchscreen": false, "brightness_nits": 400, "refresh_rate_hz": 60, "color_gamut_percent": 100, "diagonal_size_inches": 14}], "refresh_rate_hz": 60}
124	4	Display	Display Option 5	35.6 cm (14") diagonal, WUXGA (1920 x 1200), IPS, anti-glare, 300 nits, 45% NTSC	\N	2025-09-25 20:35:03.213623+00	{"displays": [{"panel_type": "IPS", "resolution": "1920x1200", "color_space": "NTSC", "aspect_ratio": "16:10", "is_touchscreen": false, "brightness_nits": 300, "refresh_rate_hz": 60, "color_gamut_percent": 45, "diagonal_size_inches": 14}], "refresh_rate_hz": 60}
125	4	Display	Display Option 6	35.6 cm (14") diagonal, WUXGA (1920 x 1200), touch, IPS, anti-glare, 300 nits, 45% NTSC	\N	2025-09-25 20:35:03.213623+00	{"displays": [{"panel_type": "IPS", "resolution": "1920x1200", "color_space": "NTSC", "aspect_ratio": "16:10", "is_touchscreen": true, "brightness_nits": 300, "refresh_rate_hz": 60, "color_gamut_percent": 45, "diagonal_size_inches": 14}], "refresh_rate_hz": 60}
126	4	Display	Display Option 7	35.6 cm (14") diagonal, WQXGA (2560 x 1600), IPS, anti-glare, 500 nits, 100% DCI-P3	\N	2025-09-25 20:35:03.213623+00	{"displays": [{"panel_type": "IPS", "resolution": "2560x1600", "color_space": "DCI-P3", "aspect_ratio": null, "is_touchscreen": false, "brightness_nits": 500, "refresh_rate_hz": 60, "color_gamut_percent": 100, "diagonal_size_inches": 14}], "refresh_rate_hz": 60}
127	4	Graphics	Graphics Option	Integrated: Intel® Arc™ Graphics; Intel® Graphics	\N	2025-09-25 20:35:03.213623+00	{"type": "Integrated", "brand": "Intel", "model": "Intel® Arc™ Graphics", "memory_gb": null}
128	4	Graphics	Graphics Option	Discrete: NVIDIA® GeForce RTX™ 2050 Laptop GPU (4 GB GDDR6 dedicated)	\N	2025-09-25 20:35:03.213623+00	{"type": "Discrete", "brand": "NVIDIA", "model": "NVIDIA® GeForce RTX™ 2050 Laptop GPU", "memory_gb": 4}
101	3	Display	Display Option 3	39.6 cm (15.6") diagonal, FHD (1920 x 1080), narrow bezel, anti-glare, 400 nits, low power, 100% sRGB	\N	2025-09-25 20:35:03.108521+00	{"displays": [{"panel_type": null, "resolution": "1920x1080", "color_space": "sRGB", "aspect_ratio": null, "is_touchscreen": false, "brightness_nits": 400, "refresh_rate_hz": 60, "color_gamut_percent": 100, "diagonal_size_inches": 15.6}], "refresh_rate_hz": 60}
102	3	Display	Display Option 4	39.6 cm (15.6") diagonal, QHD (2560 x 1440), anti-glare, narrow bezel, 300 nits, 72% NTSC	\N	2025-09-25 20:35:03.108521+00	{"displays": [{"panel_type": null, "resolution": "2560x1440", "color_space": "NTSC", "aspect_ratio": null, "is_touchscreen": false, "brightness_nits": 300, "refresh_rate_hz": 60, "color_gamut_percent": 72, "diagonal_size_inches": 15.6}], "refresh_rate_hz": 60}
103	3	Graphics	Graphics Option	Integrated: Intel® UHD Graphics; Intel® Iris® Xᶱ Graphics	\N	2025-09-25 20:35:03.108521+00	{"type": "Integrated", "brand": "Intel", "model": "Intel® UHD Graphics", "memory_gb": null}
104	3	Graphics	Graphics Option	Discrete: NVIDIA® GeForce RTX™ 2050 Laptop GPU (4 GB GDDR6 dedicated)	\N	2025-09-25 20:35:03.108521+00	{"type": "Discrete", "brand": "NVIDIA", "model": "NVIDIA® GeForce RTX™ 2050 Laptop GPU", "memory_gb": 4}
105	3	Graphics	Graphics Option	(Support CUDA, Optimus, PhysX, GPU Boost 2.0.)	\N	2025-09-25 20:35:03.108521+00	{"type": null, "brand": null, "model": null, "memory_gb": null}
106	3	Connectivity	Ports and Connectors	2 USB Type-A 5Gbps signaling rate (1 charging, 1 power); 1 AC power; 1 HDMI 2.1; 1 stereo headphone/microphone combo jack; 1 RJ-45; 2 USB Type-C® 10Gbps signaling rate (USB Power Delivery, DisplayPort™ 2.1) ; (HDMI cable sold separately.); Optional Ports: 1 External Nano SIM slot for WWAN	\N	2025-09-25 20:35:03.108521+00	{"ports": ["2 USB Type-A 5Gbps signaling rate (1 charging, 1 power)", "1 AC power", "1 HDMI 2.1", "1 stereo headphone/microphone combo jack", "1 RJ-45", "2 USB Type-C 10Gbps signaling rate (USB Power Delivery, DisplayPort 2.1)", "1 External Nano SIM slot for WWAN"], "ethernet": true, "wireless_wan": true, "wifi_standard": null, "bluetooth_version": null}
107	3	Connectivity	Communications	(Compatible with Miracast-certified devices.); ; Realtek RTL8111HSH-CG 10/100/1000 GbE NIC ; Intel® Wi-Fi 6E AX211 (2x2) and Bluetooth® 5.3 wireless card, non-vPro®; Realtek Wi-Fi 6E RTL8852CE 802.11a/b/g/n/ax (2x2) and Bluetooth® 5.3 wireless card ; Intel® XMM™ 7560 LTE Advanced Pro Cat 16 ; (Support on S3 AC mode only.)	\N	2025-09-25 20:35:03.108521+00	{"ports": ["Realtek RTL8111HSH-CG 10/100/1000 GbE NIC"], "ethernet": true, "wireless_wan": true, "wifi_standard": "Wi-Fi 6E", "bluetooth_version": "5.3"}
3	1	Processor	Core i3 / i5 / i7 Processor - Frequencies	1.2GHz / E-core 0.9	\N	2025-09-25 20:35:02.976136+00	{"brand": "Intel", "cores": null, "model": null, "threads": null, "cache_mb": null, "max_frequency_ghz": 1.2, "base_frequency_ghz": 0.9, "integrated_graphics": null}
6	1	Processor	Core i3-1315U - Frequencies	1.2GHz / E-core 0.9	\N	2025-09-25 20:35:02.976136+00	{"brand": "Intel", "cores": null, "model": "Core i3-1315U", "threads": null, "cache_mb": null, "max_frequency_ghz": 1.2, "base_frequency_ghz": 0.9, "integrated_graphics": null}
9	1	Processor	Core i5-1335U 10 - Frequencies	1.3GHz / E-core 0.9	\N	2025-09-25 20:35:02.976136+00	{"brand": "Intel", "cores": 10, "model": "Core i5-1335U", "threads": null, "cache_mb": null, "max_frequency_ghz": 1.3, "base_frequency_ghz": 0.9, "integrated_graphics": null}
12	1	Processor	Core i5-1340P 12 - Frequencies	1.9GHz / E-core 1.4	\N	2025-09-25 20:35:02.976136+00	{"brand": "Intel", "cores": 12, "model": "Core i5-1340P", "threads": null, "cache_mb": null, "max_frequency_ghz": 1.9, "base_frequency_ghz": 1.4, "integrated_graphics": null}
15	1	Processor	Core i513420H - Frequencies	2.1GHz / E-core 1.5	\N	2025-09-25 20:35:02.976136+00	{"brand": "Intel", "cores": null, "model": "Core i5-13420H", "threads": null, "cache_mb": null, "max_frequency_ghz": 2.1, "base_frequency_ghz": 1.5, "integrated_graphics": null}
18	1	Processor	Core i5-1345U 10 - Frequencies	1.6GHz / E-core 1.2	\N	2025-09-25 20:35:02.976136+00	{"brand": "Intel", "cores": 10, "model": "Core i5-1345U", "threads": null, "cache_mb": null, "max_frequency_ghz": 1.6, "base_frequency_ghz": 1.2, "integrated_graphics": null}
27	1	Processor	Core i7-1360P 12 - Frequencies	2.2GHz / E-core 1.6	\N	2025-09-25 20:35:02.976136+00	{"brand": "Intel", "cores": 12, "model": "Core i7-1360P", "threads": null, "cache_mb": null, "max_frequency_ghz": 2.2, "base_frequency_ghz": 1.6, "integrated_graphics": null}
30	1	Processor	Core i7-1365U 10 - Frequencies	1.8GHz / E-core 1.3	\N	2025-09-25 20:35:02.976136+00	{"brand": "Intel", "cores": 10, "model": "Core i7-1365U", "threads": null, "cache_mb": null, "max_frequency_ghz": 1.8, "base_frequency_ghz": 1.3, "integrated_graphics": null}
31	1	Graphics	Core i7-1365U 10 - Integrated Graphics	Intel® Iris® Xe Graphics	\N	2025-09-25 20:35:02.976136+00	{"type": "Integrated", "brand": "Intel", "model": "Intel® Iris® Xe Graphics", "memory_gb": null}
34	1	Processor	Core i713700H - Frequencies	2.4GHz / E-core 1.8	\N	2025-09-25 20:35:02.976136+00	{"brand": "Intel", "cores": null, "model": "Core i7-13700H", "threads": null, "cache_mb": null, "max_frequency_ghz": 2.4, "base_frequency_ghz": 1.8, "integrated_graphics": null}
35	1	Graphics	Core i713700H - Integrated Graphics	Intel® Iris® Xe Graphics	\N	2025-09-25 20:35:02.976136+00	{"type": "Integrated", "brand": "Intel", "model": "Intel® Iris® Xe Graphics", "memory_gb": null}
37	1	Memory	Memory Configuration	8GB soldered + 32GB SO-DIMM	\N	2025-09-25 20:35:02.976136+00	{"memory_type": null, "slots_total": 1, "is_dual_channel": null, "max_capacity_gb": 40, "slots_available": 1, "soldered_amount_gb": 8}
38	1	Memory	Memory Type	DDR4-3200	\N	2025-09-25 20:35:02.976136+00	{"memory_type": "DDR4-3200", "slots_total": null, "is_dual_channel": null, "max_capacity_gb": null, "slots_available": null, "soldered_amount_gb": null}
39	1	Storage	M.2 2242 Storage Option	256GB with Opal 2.0	\N	2025-09-25 20:35:02.976136+00	{"type": null, "security": "Opal 2.0", "interface": null, "capacity_gb": 256, "form_factor": null}
40	1	Physical	Weight	1.41 kg (3.11 lbs)	\N	2025-09-25 20:35:02.976136+00	{"weight_kg": 1.41, "weight_lbs": 3.11, "dimensions_mm": null, "dimensions_inches": null}
45	1	Battery	Battery Life - MobileMark® 25	8.58 hours	\N	2025-09-25 20:35:02.976136+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 8.58}
46	1	Battery	Battery Life - JEITA 2.0	15.2 hours	\N	2025-09-25 20:35:02.976136+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 15.2}
47	1	Battery	Battery Life - MobileMark® 2018	9.16 hours	\N	2025-09-25 20:35:02.976136+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 9.16}
48	1	Battery	Battery Life - MobileMark® 25	7.6 hours	\N	2025-09-25 20:35:02.976136+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 7.6}
49	1	Battery	Battery Life - JEITA 2.0	15.3 hours	\N	2025-09-25 20:35:02.976136+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 15.3}
50	1	Battery	Battery Life - MobileMark® 2018	8.18 hours	\N	2025-09-25 20:35:02.976136+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 8.18}
51	1	Battery	Battery Life - MobileMark® 25	6.7 hours	\N	2025-09-25 20:35:02.976136+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 6.7}
52	1	Battery	Battery Life - JEITA 2.0	14.9 hours	\N	2025-09-25 20:35:02.976136+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 14.9}
53	2	Processor	AMD Ryzen™ 3 / 5 / 7 Processor - Cache	2MB L2	\N	2025-09-25 20:35:03.049447+00	{"brand": "AMD", "cores": null, "model": "AMD Ryzen™ 3 / 5 / 7 Processor", "threads": null, "cache_mb": 2, "max_frequency_ghz": null, "base_frequency_ghz": null, "integrated_graphics": null}
54	2	Processor	AMD Ryzen™ 3 / 5 / 7 Processor - Frequencies	2.3GHz 4.3	\N	2025-09-25 20:35:03.049447+00	{"brand": "AMD", "cores": null, "model": "AMD Ryzen™ 3 / 5 / 7 Processor", "threads": null, "cache_mb": null, "max_frequency_ghz": 4.3, "base_frequency_ghz": 2.3, "integrated_graphics": null}
55	2	Graphics	AMD Ryzen™ 3 / 5 / 7 Processor - Integrated Graphics	AMD Radeon™ Graphics	\N	2025-09-25 20:35:03.049447+00	{"type": "Integrated", "brand": "AMD", "model": "AMD Radeon™ Graphics", "memory_gb": null}
56	2	Processor	AMD Ryzen™ 3 7330U 4 - Cache	2MB L2	\N	2025-09-25 20:35:03.049447+00	{"brand": "AMD", "cores": null, "model": "AMD Ryzen™ 3 7330U", "threads": null, "cache_mb": 2, "max_frequency_ghz": null, "base_frequency_ghz": null, "integrated_graphics": null}
57	2	Processor	AMD Ryzen™ 3 7330U 4 - Frequencies	2.3GHz 4.3	\N	2025-09-25 20:35:03.049447+00	{"brand": "AMD", "cores": 4, "model": "AMD Ryzen™ 3 7330U", "threads": null, "cache_mb": null, "max_frequency_ghz": 4.3, "base_frequency_ghz": 2.3, "integrated_graphics": null}
58	2	Graphics	AMD Ryzen™ 3 7330U 4 - Integrated Graphics	AMD Radeon™ Graphics	\N	2025-09-25 20:35:03.049447+00	{"type": "Integrated", "brand": "AMD", "model": "AMD Radeon™ Graphics", "memory_gb": null}
59	2	Processor	AMD Ryzen™ 5 5625U 6 - Cache	3MB L2	\N	2025-09-25 20:35:03.049447+00	{"brand": "AMD", "cores": 6, "model": "AMD Ryzen™ 5 5625U", "threads": null, "cache_mb": 3, "max_frequency_ghz": null, "base_frequency_ghz": null, "integrated_graphics": null}
60	2	Processor	AMD Ryzen™ 5 5625U 6 - Frequencies	2.3GHz 4.3	\N	2025-09-25 20:35:03.049447+00	{"brand": "AMD", "cores": 6, "model": "AMD Ryzen™ 5 5625U", "threads": null, "cache_mb": null, "max_frequency_ghz": 4.3, "base_frequency_ghz": 2.3, "integrated_graphics": null}
69	2	Processor	AMD Ryzen™ 7 7730U 8 - Frequencies	2.0GHz 4.5	\N	2025-09-25 20:35:03.049447+00	{"brand": "AMD", "cores": 8, "model": "AMD Ryzen™ 7 7730U", "threads": null, "cache_mb": null, "max_frequency_ghz": 4.5, "base_frequency_ghz": 2.0, "integrated_graphics": null}
70	2	Graphics	AMD Ryzen™ 7 7730U 8 - Integrated Graphics	AMD Radeon™ Graphics	\N	2025-09-25 20:35:03.049447+00	{"type": "Integrated", "brand": "AMD", "model": "AMD Radeon™ Graphics", "memory_gb": null}
72	2	Memory	Memory Configuration	8GB soldered + 32GB SO-DIMM	\N	2025-09-25 20:35:03.049447+00	{"memory_type": null, "slots_total": 1, "is_dual_channel": null, "max_capacity_gb": 40, "slots_available": 1, "soldered_amount_gb": 8}
73	2	Memory	Memory Type	DDR4-3200	\N	2025-09-25 20:35:03.049447+00	{"memory_type": "DDR4-3200", "slots_total": null, "is_dual_channel": null, "max_capacity_gb": null, "slots_available": null, "soldered_amount_gb": null}
74	2	Physical	Weight	1.41 kg (3.11 lbs)	\N	2025-09-25 20:35:03.049447+00	{"weight_kg": 1.41, "weight_lbs": 3.11, "dimensions_mm": null, "dimensions_inches": null}
75	2	Physical	Weight	1.43 kg (3.15 lbs)	\N	2025-09-25 20:35:03.049447+00	{"weight_kg": 1.43, "weight_lbs": 3.15, "dimensions_mm": null, "dimensions_inches": null}
76	2	Battery	Battery Option	47Wh Li-ion with Rapid Charge	\N	2025-09-25 20:35:03.049447+00	{"cells": null, "chemistry": "Li-ion", "capacity_wh": 47, "rapid_charge": true, "test_results": [], "battery_life_hours": null}
77	2	Battery	Battery Option	57Wh Li-ion with Rapid Charge	\N	2025-09-25 20:35:03.049447+00	{"cells": null, "chemistry": "Li-ion", "capacity_wh": 57, "rapid_charge": true, "test_results": [], "battery_life_hours": null}
78	2	Battery	Battery Life - MobileMark® 2018	15.03 hours	\N	2025-09-25 20:35:03.049447+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 15.03}
79	2	Battery	Battery Life - JEITA 2.0	20.85 hours	\N	2025-09-25 20:35:03.049447+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 20.85}
80	2	Battery	Battery Life - MobileMark® 2018	13.73 hours	\N	2025-09-25 20:35:03.049447+00	{"cells": null, "chemistry": null, "capacity_wh": null, "rapid_charge": null, "test_results": [], "battery_life_hours": 13.73}
84	3	Processor	Processor Family	Intel® Pentium® processor	\N	2025-09-25 20:35:03.108521+00	{"brand": "Intel", "cores": null, "model": "Intel® Pentium® processor", "threads": null, "cache_mb": null, "max_frequency_ghz": null, "base_frequency_ghz": null, "integrated_graphics": null}
85	3	Processor	Processor Family	13th Generation Intel® Core™ i7 processor	\N	2025-09-25 20:35:03.108521+00	{"brand": "Intel", "cores": null, "model": "13th Generation Intel® Core™ i7", "threads": null, "cache_mb": null, "max_frequency_ghz": null, "base_frequency_ghz": null, "integrated_graphics": null}
86	3	Processor	Processor Family	13th Generation Intel® Core™ i5 processor	\N	2025-09-25 20:35:03.108521+00	{"brand": "Intel", "cores": null, "model": "13th Generation Intel® Core™ i5 processor", "threads": null, "cache_mb": null, "max_frequency_ghz": null, "base_frequency_ghz": null, "integrated_graphics": null}
87	3	Processor	Processor Family	13th Generation Intel® Core™ i3 processor	\N	2025-09-25 20:35:03.108521+00	{"brand": "Intel", "cores": null, "model": "13th Generation Intel® Core™ i3 processor", "threads": null, "cache_mb": null, "max_frequency_ghz": null, "base_frequency_ghz": null, "integrated_graphics": null}
88	3	Processor	Intel® Core™ i7-1355U	1.2 GHz E-core base frequency, 1.7 GHz P-core base frequency, up to 3.7 GHz E-core Max Turbo frequency, up to 5.0 GHz Pcore Max Turbo frequency, 12 MB L3 cache, 2 P-cores and 8 E-cores, 12 threads	\N	2025-09-25 20:35:03.108521+00	{"brand": "Intel", "cores": 10, "model": "Intel® Core™ i7-1355U", "threads": 12, "cache_mb": 12, "max_frequency_ghz": 5.0, "base_frequency_ghz": 1.2, "integrated_graphics": null}
89	3	Processor	Intel® Core™ i5-1335U	0.9 GHz E-core base frequency, 1.3 GHz P-core base frequency, up to 3.4 GHz E-core Max Turbo frequency, up to 4.6 GHz Pcore Max Turbo frequency, 12 MB L3 cache, 2 P-cores and 8 E-cores, 12 threads	\N	2025-09-25 20:35:03.108521+00	{"brand": "Intel", "cores": 10, "model": "Intel® Core™ i5-1335U", "threads": 12, "cache_mb": 12, "max_frequency_ghz": 4.6, "base_frequency_ghz": 0.9, "integrated_graphics": null}
90	3	Processor	Intel® Core™ i3-1340P with Intel® UHD Graphics	0.9 GHz E-core base frequency, 1.2 GHz P-core base frequency, up to 3.3 GHz E-core Max Turbo frequency, up to 4.5 GHz P-core Max Turbo frequency, 10 MB L3 cache, 2 P-cores and 4 E-cores, 6 threads	\N	2025-09-25 20:35:03.108521+00	{"brand": "Intel", "cores": 6, "model": "Intel® Core™ i3-1340P", "threads": 6, "cache_mb": 10, "max_frequency_ghz": 4.5, "base_frequency_ghz": 0.9, "integrated_graphics": "Intel® UHD Graphics"}
91	3	Processor	Intel® Core™ i7-1360P	1.6 GHz E-core base frequency, 2.2 GHz P-core base frequency, up to 3.7 GHz E-core Max Turbo frequency, up to 5.0 GHz Pcore Max Turbo frequency, 18 MB L3 cache, 4 P-cores and 8 E-cores, 16 threads	\N	2025-09-25 20:35:03.108521+00	{"brand": "Intel", "cores": 12, "model": "Intel® Core™ i7-1360P", "threads": 16, "cache_mb": 18, "max_frequency_ghz": 5.0, "base_frequency_ghz": 1.6, "integrated_graphics": null}
92	3	Processor	Intel® Core™ i5-1340P	1.4 GHz E-core base frequency, 1.9 GHz P-core base frequency, up to 3.4 GHz E-core Max Turbo frequency, up to 4.6 GHz Pcore Max Turbo frequency, 12 MB L3 cache, 4 P-cores and 8 E-cores, 16 threads	\N	2025-09-25 20:35:03.108521+00	{"brand": "Intel", "cores": 12, "model": "Intel® Core™ i5-1340P", "threads": 16, "cache_mb": 12, "max_frequency_ghz": 4.6, "base_frequency_ghz": 1.4, "integrated_graphics": null}
93	3	Processor	Intel® Core™ i5-1334U	0.9 GHz E-core base frequency, 1.3 GHz P-core base frequency, up to 3.4 GHz E-core Max Turbo frequency, up to 4.6 GHz Pcore Max Turbo frequency, 12 MB L3 cache, 2 P-cores and 8 E-core, 12 threads	\N	2025-09-25 20:35:03.108521+00	{"brand": "Intel", "cores": 10, "model": "Intel® Core™ i5-1334U", "threads": 12, "cache_mb": 12, "max_frequency_ghz": 4.6, "base_frequency_ghz": 0.9, "integrated_graphics": null}
94	3	Memory	Maximum Memory	32 GB DDR4-3200 MHz RAM; (Transfer rates up to 3200 MT/s.); Both slots are accessible/upgradeable by IT or self-maintainers only. Supports dual channel memory.	\N	2025-09-25 20:35:03.108521+00	{"memory_type": "DDR4-3200", "slots_total": 2, "is_dual_channel": true, "max_capacity_gb": 32, "slots_available": 2, "soldered_amount_gb": null}
95	3	Memory	Memory Slots	2 SODIMM	\N	2025-09-25 20:35:03.108521+00	{"memory_type": null, "slots_total": 2, "is_dual_channel": null, "max_capacity_gb": null, "slots_available": null, "soldered_amount_gb": null}
96	3	Storage	Storage Option	up to 1 TB PCIe® NVMe™ M.2 SSD TLC	\N	2025-09-25 20:35:03.108521+00	{"type": "SSD", "security": null, "interface": "PCIe NVMe", "capacity_gb": 1000, "form_factor": "M.2"}
97	3	Storage	Storage Option	128 GB up to 512 GB PCIe® NVMe™ Value SSD	\N	2025-09-25 20:35:03.108521+00	{"type": "SSD", "security": null, "interface": "PCIe NVMe", "capacity_gb": [128, 512], "form_factor": null}
98	3	Display	Display Size	39.6 cm (15.6")	\N	2025-09-25 20:35:03.108521+00	{"displays": [{"panel_type": null, "resolution": null, "color_space": null, "aspect_ratio": null, "is_touchscreen": false, "brightness_nits": null, "refresh_rate_hz": 60, "color_gamut_percent": null, "diagonal_size_inches": 15.6}], "refresh_rate_hz": 60}
99	3	Display	Display Option 1	size (diagonal, metric) 39.6 cm (15.6") Display 39.6 cm (15.6") diagonal, FHD (1920 x 1080), narrow bezel, anti-glare, 250 nits, 45% NTSC	\N	2025-09-25 20:35:03.108521+00	{"displays": [{"panel_type": null, "resolution": "1920x1080", "color_space": "NTSC", "aspect_ratio": null, "is_touchscreen": false, "brightness_nits": 250, "refresh_rate_hz": 60, "color_gamut_percent": 45, "diagonal_size_inches": 15.6}], "refresh_rate_hz": 60}
100	3	Display	Display Option 2	39.6 cm (15.6") diagonal, FHD (1920 x 1080), touch, narrow bezel, anti-glare, 250 nits, 45% NTSC	\N	2025-09-25 20:35:03.108521+00	{"displays": [{"panel_type": null, "resolution": "1920x1080", "color_space": "NTSC", "aspect_ratio": null, "is_touchscreen": true, "brightness_nits": 250, "refresh_rate_hz": 60, "color_gamut_percent": 45, "diagonal_size_inches": 15.6}], "refresh_rate_hz": 60}
108	3	Physical	Dimensions	35.94 x 23.39 x 1.99 cm; 6.9 x 48.3 x 30.5 cm (Package)	\N	2025-09-25 20:35:03.108521+00	{"weight_kg": null, "weight_lbs": null, "dimensions_mm": {"depth": 233.9, "width": 359.4, "height": 19.9}, "dimensions_inches": null}
109	3	Physical	Weight	Starting at 1.79 kg; (Weight will vary by configuration. Does not include power adapter.)	\N	2025-09-25 20:35:03.108521+00	{"weight_kg": 1.79, "weight_lbs": null, "dimensions_mm": null, "dimensions_inches": null}
110	4	Processor	Processor Family	Intel® Core™ Ultra 5 processor	\N	2025-09-25 20:35:03.213623+00	{"brand": "Intel", "cores": null, "model": "Intel® Core™ Ultra 5 processor", "threads": null, "cache_mb": null, "max_frequency_ghz": null, "base_frequency_ghz": null, "integrated_graphics": null}
111	4	Processor	Processor Family	Intel® Core™ Ultra 7 processor	\N	2025-09-25 20:35:03.213623+00	{"brand": "Intel", "cores": null, "model": "Intel® Core™ Ultra 7 processor", "threads": null, "cache_mb": null, "max_frequency_ghz": null, "base_frequency_ghz": null, "integrated_graphics": null}
112	4	Processor	Intel® Core™ Ultra 7 155H	up to 3.8 GHz E-core Max Turbo frequency, up to 4.8 GHz P-core Max Turbo frequency, 24 MB L3 cache, 6 Pcores and 8 E-cores, 22 threads	\N	2025-09-25 20:35:03.213623+00	{"brand": "Intel", "cores": 14, "model": "Intel® Core™ Ultra 7 155H", "threads": 22, "cache_mb": 24, "max_frequency_ghz": 4.8, "base_frequency_ghz": null, "integrated_graphics": null}
113	4	Processor	Intel® Core™ Ultra 5 125H	up to 3.6 GHz E-core Max Turbo frequency, up to 4.5 GHz P-core Max Turbo frequency, 18 MB L3 cache, 4 Pcores and 8 E-cores, 18 threads	\N	2025-09-25 20:35:03.213623+00	{"brand": "Intel", "cores": 12, "model": "Intel® Core™ Ultra 5 125H", "threads": 18, "cache_mb": 18, "max_frequency_ghz": 4.5, "base_frequency_ghz": null, "integrated_graphics": null}
114	4	Processor	Intel® Core™ Ultra 7 155U	up to 3.8 GHz E-core Max Turbo frequency, up to 4.8 GHz P-core Max Turbo frequency, 12 MB L3 cache, 2 Pcores and 8 E-cores, 14 threads	\N	2025-09-25 20:35:03.213623+00	{"brand": "Intel", "cores": 10, "model": "Intel® Core™ Ultra 7 155U", "threads": 14, "cache_mb": 12, "max_frequency_ghz": 4.8, "base_frequency_ghz": null, "integrated_graphics": null}
115	4	Processor	Intel® Core™ Ultra 5 125U	up to 3.6 GHz E-core Max Turbo frequency, up to 4.3 GHz P-core Max Turbo frequency, 12 MB L3 cache, 2 Pcores and 8 E-cores, 14 threads	\N	2025-09-25 20:35:03.213623+00	{"brand": "Intel", "cores": 10, "model": "Intel® Core™ Ultra 5 125U", "threads": 14, "cache_mb": 12, "max_frequency_ghz": 4.3, "base_frequency_ghz": null, "integrated_graphics": null}
116	4	Memory	Maximum Memory	32 GB DDR5-5600 MT/s RAM; (Transfer rates up to 5600 MT/s.) Dual channel support.	\N	2025-09-25 20:35:03.213623+00	{"memory_type": "DDR5-5600", "slots_total": null, "is_dual_channel": true, "max_capacity_gb": 32, "slots_available": null, "soldered_amount_gb": null}
117	4	Memory	Memory Slots	2 SODIMM	\N	2025-09-25 20:35:03.213623+00	{"memory_type": null, "slots_total": 2, "is_dual_channel": null, "max_capacity_gb": null, "slots_available": 2, "soldered_amount_gb": null}
118	4	Storage	Storage Option	512 GB up to 1 TB PCIe® Gen4x4 NVMe™ M.2 SSD	\N	2025-09-25 20:35:03.213623+00	{"type": "SSD", "security": null, "interface": "PCIe Gen4x4 NVMe", "capacity_gb": [512, 1000], "form_factor": "M.2"}
119	4	Storage	Storage Option	up to 256 GB PCIe® NVMe™ Value SSD	\N	2025-09-25 20:35:03.213623+00	{"type": "SSD", "security": null, "interface": "PCIe NVMe", "capacity_gb": 256, "form_factor": null}
120	4	Display	Display Option 1	size (diagonal, metric) 35.6 cm (14") Display 14" diagonal, WUXGA (1920 x 1200), IPS, anti-glare, 400 nits, low power, 100% sRGB with HP Eye Ease	\N	2025-09-25 20:35:03.213623+00	{"displays": [{"panel_type": "IPS", "resolution": "1920x1200", "color_space": "sRGB", "aspect_ratio": "16:10", "is_touchscreen": false, "brightness_nits": 400, "refresh_rate_hz": 60, "color_gamut_percent": 100, "diagonal_size_inches": 14}], "refresh_rate_hz": 60}
131	4	Physical	Dimensions	12.54 x 8.83 x 0.43 in (front); 12.54 x 8.83 x 0.67 in (rear); 31.86 x 22.44 x 1.09 cm (front); 31.86 x 22.43 x 1.7 cm (rear); (Front height measurement is near the front edge where the chassis bottom cover taper begins. Back height measurement is near the back edge where the chassis bottom cover taper ends.); 2.71 x 17.67 x 12 in 6.9 x 44.9 x 30.5 cm (Package)	\N	2025-09-25 20:35:03.213623+00	{"dimensions_mm": [{"part": "front", "depth": 224.4, "width": 318.6, "height": 10.9}, {"part": "rear", "depth": 224.3, "width": 318.6, "height": 17.0}, {"part": "package", "depth": 449.0, "width": 690.0, "height": 305.0}], "dimensions_inches": [{"part": "front", "depth": 8.83, "width": 12.54, "height": 0.43}, {"part": "rear", "depth": 8.83, "width": 12.54, "height": 0.67}, {"part": "package", "depth": 17.67, "width": 2.71, "height": 12.0}]}
132	4	Physical	Weight	Starting at 3.08 lb; Starting at 1.39 kg; (Weight will vary by configuration. Does not include power adapter.)	\N	2025-09-25 20:35:03.213623+00	{"weight_kg": 1.39, "weight_lbs": 3.08, "dimensions_mm": null, "dimensions_inches": null}
\.


--
-- Name: laptops_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.laptops_id_seq', 4, true);


--
-- Name: price_snapshots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.price_snapshots_id_seq', 188, true);


--
-- Name: questions_answers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.questions_answers_id_seq', 1, false);


--
-- Name: reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.reviews_id_seq', 105, true);


--
-- Name: specifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.specifications_id_seq', 132, true);


--
-- Name: laptops laptops_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.laptops
    ADD CONSTRAINT laptops_pkey PRIMARY KEY (id);


--
-- Name: price_snapshots price_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.price_snapshots
    ADD CONSTRAINT price_snapshots_pkey PRIMARY KEY (id);


--
-- Name: questions_answers questions_answers_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.questions_answers
    ADD CONSTRAINT questions_answers_pkey PRIMARY KEY (id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- Name: specifications specifications_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.specifications
    ADD CONSTRAINT specifications_pkey PRIMARY KEY (id);


--
-- Name: laptops unique_laptop_variant; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.laptops
    ADD CONSTRAINT unique_laptop_variant UNIQUE (brand, model_name, variant);


--
-- Name: idx_availability; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX idx_availability ON public.price_snapshots USING btree (availability_status);


--
-- Name: idx_laptop_category; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX idx_laptop_category ON public.specifications USING btree (laptop_id, category);


--
-- Name: idx_laptop_price_time; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX idx_laptop_price_time ON public.price_snapshots USING btree (laptop_id, scraped_at);


--
-- Name: idx_laptop_qa; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX idx_laptop_qa ON public.questions_answers USING btree (laptop_id);


--
-- Name: idx_laptop_rating; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX idx_laptop_rating ON public.reviews USING btree (laptop_id, rating);


--
-- Name: idx_qa_date; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX idx_qa_date ON public.questions_answers USING btree (question_date);


--
-- Name: idx_review_date; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX idx_review_date ON public.reviews USING btree (review_date);


--
-- Name: idx_spec_name; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX idx_spec_name ON public.specifications USING btree (specification_name);


--
-- Name: laptops update_laptops_updated_at; Type: TRIGGER; Schema: public; Owner: myuser
--

CREATE TRIGGER update_laptops_updated_at BEFORE UPDATE ON public.laptops FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: price_snapshots price_snapshots_laptop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.price_snapshots
    ADD CONSTRAINT price_snapshots_laptop_id_fkey FOREIGN KEY (laptop_id) REFERENCES public.laptops(id) ON DELETE CASCADE;


--
-- Name: questions_answers questions_answers_laptop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.questions_answers
    ADD CONSTRAINT questions_answers_laptop_id_fkey FOREIGN KEY (laptop_id) REFERENCES public.laptops(id) ON DELETE CASCADE;


--
-- Name: reviews reviews_laptop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_laptop_id_fkey FOREIGN KEY (laptop_id) REFERENCES public.laptops(id) ON DELETE CASCADE;


--
-- Name: specifications specifications_laptop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.specifications
    ADD CONSTRAINT specifications_laptop_id_fkey FOREIGN KEY (laptop_id) REFERENCES public.laptops(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict Ha57yTEqbL1zDTSkq9PUT5xiuBcJzQtnur26mncY71y8Pg2XAtvOckzZlnc9XKE

