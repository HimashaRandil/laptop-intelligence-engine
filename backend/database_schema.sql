-- Core laptops table (treats Intel/AMD as separate laptops)
CREATE TABLE laptops (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL, -- 'Lenovo' or 'HP'
    model_name VARCHAR(200) NOT NULL, -- 'ThinkPad E14 Gen 5'
    variant VARCHAR(100), -- 'Intel' or 'AMD'
    full_model_name VARCHAR(300) NOT NULL, -- 'ThinkPad E14 Gen 5 (Intel)'
    product_page_url TEXT,
    pdf_spec_url TEXT NOT NULL,
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_laptop_variant UNIQUE(brand, model_name, variant)
);

-- Technical specifications (flexible key-value store)
CREATE TABLE specifications (
    id SERIAL PRIMARY KEY,
    laptop_id INTEGER NOT NULL REFERENCES laptops(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL, -- 'Processor', 'Memory', 'Display', etc.
    specification_name VARCHAR(200) NOT NULL, -- 'CPU Model', 'RAM Size', 'Screen Size'
    specification_value TEXT NOT NULL, -- Raw value as extracted
    unit VARCHAR(20), -- 'GB', 'inch', 'GHz', etc. (optional)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE specifications ADD COLUMN structured_value JSONB;

-- Price history (time series for trends)
CREATE TABLE price_snapshots (
    id SERIAL PRIMARY KEY,
    laptop_id INTEGER NOT NULL REFERENCES laptops(id) ON DELETE CASCADE,
    price DECIMAL(10, 2), -- NULL if price not available
    currency VARCHAR(3) DEFAULT 'USD',
    availability_status VARCHAR(50), -- 'In Stock', 'Out of Stock', 'Limited', etc.
    shipping_info TEXT, -- 'Free shipping', '2-3 days', etc.
    promotion_text TEXT, -- '20% off', 'Free upgrade', etc.
    configuration_summary TEXT, -- Stores details like "Core Ultra 5 / 16GB RAM / 512GB SSD"
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Customer reviews (simple structure for MVP)
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    laptop_id INTEGER NOT NULL REFERENCES laptops(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_title TEXT,
    review_text TEXT,
    reviewer_name VARCHAR(200),
    reviewer_verified BOOLEAN DEFAULT FALSE,
    review_date DATE,
    helpful_count INTEGER DEFAULT 0,
    configuration_summary TEXT, -- Stores details for the model being reviewed
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Q&A section from product pages 
-- Will be focusing on this after the main features are done
CREATE TABLE questions_answers (
    id SERIAL PRIMARY KEY,
    laptop_id INTEGER NOT NULL REFERENCES laptops(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    answer_text TEXT,
    asker_name VARCHAR(200),
    answerer_name VARCHAR(200),
    question_date DATE,
    answer_date DATE,
    helpful_count INTEGER DEFAULT 0,
    configuration_summary TEXT, -- Stores details for the model being asked about
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- === Indexes for Performance (Moved here from inside the tables) ===
CREATE INDEX idx_laptop_category ON specifications (laptop_id, category);
CREATE INDEX idx_spec_name ON specifications (specification_name);
CREATE INDEX idx_laptop_price_time ON price_snapshots (laptop_id, scraped_at);
CREATE INDEX idx_availability ON price_snapshots (availability_status);
CREATE INDEX idx_laptop_rating ON reviews (laptop_id, rating);
CREATE INDEX idx_review_date ON reviews (review_date);
CREATE INDEX idx_laptop_qa ON questions_answers (laptop_id);
CREATE INDEX idx_qa_date ON questions_answers (question_date);

-- Triggers to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_laptops_updated_at 
    BEFORE UPDATE ON laptops 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE VIEW laptop_latest_prices AS
SELECT DISTINCT ON (laptop_id) 
    laptop_id,
    price,
    currency,
    availability_status,
    promotion_text,
    configuration_summary,
    scraped_at
FROM price_snapshots
ORDER BY laptop_id, scraped_at DESC;

CREATE VIEW laptop_review_summary AS
SELECT 
    laptop_id,
    COUNT(*) as total_reviews,
    AVG(rating)::DECIMAL(3,2) as average_rating,
    COUNT(CASE WHEN rating = 5 THEN 1 END) as five_star_count,
    COUNT(CASE WHEN rating = 1 THEN 1 END) as one_star_count
FROM reviews
GROUP BY laptop_id;

-- Initial data structure (to be populated by our scripts)
-- Example of how our 4 laptops will be stored:
INSERT INTO laptops (brand, model_name, variant, full_model_name, product_page_url, pdf_spec_url, image_url) VALUES
('Lenovo', 'ThinkPad E14 Gen 5', 'Intel', 'ThinkPad E14 Gen 5 (Intel)','https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpade/thinkpad-e14-gen-5-14-inch-intel/len101t0064' ,'https://psref.lenovo.com/syspool/Sys/PDF/ThinkPad/ThinkPad_E14_Gen_5_Intel/ThinkPad_E14_Gen_5_Intel_Spec.PDF','https://p3-ofp.static.pub/fes/cms/2023/05/15/h5cqimqsg3i95ffichjsp8qz9wun5h434750.jpg'),
('Lenovo', 'ThinkPad E14 Gen 5', 'AMD', 'ThinkPad E14 Gen 5 (AMD)', 'https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpade/thinkpad-e14-gen-5-14-inch-amd/len101t0068?orgRef=https%253A%252F%252Fwww.google.com%252F&srsltid=AfmBOoqAS4HFde0cPIpvn4VZodEMsRkvV0akOcfFq_K6PXjuPX2CXlMV','https://psref.lenovo.com/syspool/Sys/PDF/ThinkPad/ThinkPad_E14_Gen_5_AMD/ThinkPad_E14_Gen_5_AMD_Spec.pdf','https://p1-ofp.static.pub/fes/cms/2023/05/30/t7l1v4d7clb4flto8dyzrltuhnyx6y985674.jpg'),
('HP', 'ProBook 450', 'G10', 'HP ProBook 450 G10','https://www.hp.com/us-en/shop/pdp/hp-probook-450-156-inch-g10-notebook-pc-wolf-pro-security-edition-p-8l0e0ua-aba-1' ,'https://h20195.www2.hp.com/v2/GetPDF.aspx/c08504822.pdf', 'https://hp.widen.net/content/wvqwdaw4fy/jpeg/wvqwdaw4fy.jpg?w=1500&dpi=300'),
('HP', 'ProBook 440', 'G11', 'HP ProBook 440 G11', 'https://www.hp.com/us-en/shop/mdp/pro-352502--1/probook-440','https://h20195.www2.hp.com/v2/getpdf.aspx/c08947328.pdf', 'https://www.hp.com/wcsstore/hpusstore/Treatment/mdps/Q2FY23_Probook_Series_G10_Redesign/Commercial.jpg');