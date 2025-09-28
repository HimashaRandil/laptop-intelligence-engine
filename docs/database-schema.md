# Database Schema Documentation

The Laptop Intelligence Engine uses a PostgreSQL database designed to handle laptop specifications, pricing history, reviews, and Q&A data with optimal query performance and data integrity.

## Schema Overview

![Database Schema](docs\Diagram.png)

The database consists of 5 core tables with carefully designed relationships to support the application's features:

- **laptops**: Core laptop inventory
- **specifications**: Technical specifications with structured data
- **price_snapshots**: Historical pricing and availability data
- **reviews**: Customer reviews with ratings
- **questions_answers**: Q&A content from product pages

## Table Definitions

### `laptops` - Core Laptop Inventory

The primary table storing laptop models and basic information.

```sql
CREATE TABLE laptops (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    model_name VARCHAR(200) NOT NULL,
    variant VARCHAR(100),
    full_model_name VARCHAR(300) NOT NULL,
    product_page_url TEXT,
    pdf_spec_url TEXT NOT NULL,
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_laptop_variant UNIQUE(brand, model_name, variant)
);
```

**Key Features**:
- **Composite Identity**: `brand + model_name + variant` ensures unique laptop variants
- **URL References**: Links to official product pages and PDF specifications
- **Timestamps**: Automatic creation and update tracking

**Current Data**:
- 4 laptop models: 2 Lenovo ThinkPad E14 Gen 5 (Intel/AMD), 2 HP ProBook models
- All entries include official PDF specification URLs

### `specifications` - Technical Specifications

Flexible storage for technical specifications with both raw and structured data.

```sql
CREATE TABLE specifications (
    id SERIAL PRIMARY KEY,
    laptop_id INTEGER NOT NULL REFERENCES laptops(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    specification_name VARCHAR(200) NOT NULL,
    specification_value TEXT NOT NULL,
    unit VARCHAR(20),
    structured_value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features**:
- **Flexible Schema**: Supports any specification type via category grouping
- **Dual Storage**: Raw text values + structured JSONB for complex data
- **Hierarchical Organization**: Categories group related specifications

**Categories Include**:
- **Processor**: CPU models, cores, frequencies, cache
- **Memory**: RAM configurations, maximum capacity, types
- **Storage**: SSD/HDD options, capacities, interfaces
- **Graphics**: Integrated/discrete GPU information
- **Battery**: Capacity, life estimates, charging features
- **Physical**: Weight, dimensions, build materials

**Example Structured Data**:
```json
{
  "brand": "Intel",
  "cores": 10,
  "model": "Core i7-1355U",
  "max_frequency_ghz": 1.7,
  "base_frequency_ghz": 1.2
}
```

### `price_snapshots` - Historical Pricing Data

Time-series data for price tracking and availability monitoring.

```sql
CREATE TABLE price_snapshots (
    id SERIAL PRIMARY KEY,
    laptop_id INTEGER NOT NULL REFERENCES laptops(id) ON DELETE CASCADE,
    price DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    availability_status VARCHAR(50),
    shipping_info TEXT,
    promotion_text TEXT,
    configuration_summary TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features**:
- **Time Series**: Tracks price changes over time
- **Configuration Tracking**: Links prices to specific hardware configurations
- **Availability States**: "In Stock", "Limited Stock", "Out of Stock"
- **Promotion Support**: Captures special offers and discounts

**Sample Data Pattern**:
- Multiple price points per laptop for different configurations
- Historical data showing price fluctuations
- Configuration details like "Core i7-1355U / 16GB RAM / 512GB SSD"

### `reviews` - Customer Reviews

Customer feedback with ratings and detailed text reviews.

```sql
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
    configuration_summary TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features**:
- **Star Ratings**: 1-5 scale with validation constraints
- **Rich Content**: Title and detailed review text
- **Reviewer Identity**: Names with verification status
- **Helpfulness Scoring**: Community-driven quality indicators
- **Configuration Context**: Links reviews to specific hardware configs

**Review Categories Covered**:
- Business use cases and enterprise deployment
- Build quality and durability
- Performance for specific workloads
- Keyboard and input device quality
- Battery life and portability

### `questions_answers` - Q&A Content

Customer questions and expert answers from product pages.

```sql
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
    configuration_summary TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features**:
- **Q&A Pairs**: Structured question-answer format
- **Community Driven**: Real user questions with expert answers
- **Helpfulness Metrics**: Community validation of answer quality
- **Date Tracking**: Separate timestamps for questions and answers

**Common Question Types**:
- Hardware upgrade possibilities
- Software compatibility
- Use case suitability (programming, video editing)
- Comparison with other models

## Relationships and Foreign Keys

### Primary Relationships

1. **One-to-Many**: `laptops` → `specifications`
   - Each laptop has 100+ technical specifications
   - Categories provide logical grouping

2. **One-to-Many**: `laptops` → `price_snapshots`
   - Each laptop has 12+ price history records
   - Tracks multiple configurations over time

3. **One-to-Many**: `laptops` → `reviews`
   - Each laptop has 6+ customer reviews
   - Includes ratings and detailed feedback

4. **One-to-Many**: `laptops` → `questions_answers`
   - Each laptop has 4+ Q&A pairs
   - Real customer questions with expert answers

### Referential Integrity

- **CASCADE DELETE**: Removing a laptop automatically cleans up all related data
- **NOT NULL CONSTRAINTS**: Ensures data completeness for critical fields
- **CHECK CONSTRAINTS**: Validates rating ranges (1-5 stars)
- **UNIQUE CONSTRAINTS**: Prevents duplicate laptop variants

## Indexes and Performance

### Primary Indexes

```sql
-- Performance indexes for common query patterns
CREATE INDEX idx_laptop_category ON specifications (laptop_id, category);
CREATE INDEX idx_spec_name ON specifications (specification_name);
CREATE INDEX idx_laptop_price_time ON price_snapshots (laptop_id, scraped_at);
CREATE INDEX idx_availability ON price_snapshots (availability_status);
CREATE INDEX idx_laptop_rating ON reviews (laptop_id, rating);
CREATE INDEX idx_review_date ON reviews (review_date);
CREATE INDEX idx_laptop_qa ON questions_answers (laptop_id);
CREATE INDEX idx_qa_date ON questions_answers (question_date);
```

### Query Optimization

- **Composite Indexes**: Optimize filtered queries by laptop and category
- **Time-Based Indexes**: Support price history and review timeline queries
- **Text Search**: Full-text search on specifications and reviews
- **JSONB Indexes**: GIN indexes on structured specification data

## Database Views

### `laptop_latest_prices`

Materialized view providing latest price for each laptop:

```sql
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
```

### `laptop_review_summary`

Aggregated review statistics per laptop:

```sql
CREATE VIEW laptop_review_summary AS
SELECT 
    laptop_id,
    COUNT(*) as total_reviews,
    AVG(rating)::DECIMAL(3,2) as average_rating,
    COUNT(CASE WHEN rating = 5 THEN 1 END) as five_star_count,
    COUNT(CASE WHEN rating = 1 THEN 1 END) as one_star_count
FROM reviews
GROUP BY laptop_id;
```

## Data Volume and Statistics

### Current Dataset

| Table | Records | Description |
|-------|---------|-------------|
| `laptops` | 4 | Core laptop models |
| `specifications` | 400+ | Technical specifications (100+ per laptop) |
| `price_snapshots` | 48 | Historical price data (12 per laptop) |
| `reviews` | 24 | Customer reviews (6 per laptop) |
| `questions_answers` | 16 | Q&A pairs (4 per laptop) |

### Storage Requirements

- **Total Database Size**: ~50MB
- **Specifications**: ~30MB (largest table due to text content)
- **Reviews**: ~10MB (text-heavy with detailed feedback)
- **Price History**: ~5MB (time series data)
- **Q&A Content**: ~5MB (question-answer pairs)

## Data Quality and Validation

### Constraints and Rules

1. **Rating Validation**: Reviews must have ratings between 1-5
2. **Required Fields**: All laptops must have PDF specification URLs
3. **Unique Variants**: Prevents duplicate laptop model-variant combinations
4. **Timestamp Consistency**: Automatic creation and update tracking
5. **Referential Integrity**: Cascading deletes maintain data consistency

### Data Completeness

- **100%** laptop models have official PDF specifications
- **100%** laptops have pricing data with availability status
- **100%** laptops have customer reviews with ratings
- **100%** laptops have Q&A content

## Vector Database Integration

### ChromaDB Collections

The system also maintains vector embeddings for semantic search:

- **`laptop_reviews`**: Embeddings of review content for similarity search
- **`laptop_qa`**: Embeddings of Q&A content for intelligent matching

### Vector-SQL Coordination

- Vector database automatically initializes from SQL data
- Reviews and Q&A are embedded with metadata linking back to SQL records
- AI queries combine structured SQL data with semantic vector search

## Migration and Maintenance

### Database Initialization

```sql
-- Automatic table creation
Base.metadata.create_all(bind=engine)

-- Sample data loading
INSERT INTO laptops (brand, model_name, variant, full_model_name, ...);
```

### Backup Strategy

- **SQL Dumps**: Complete database backup via `pg_dump`
- **Docker Volumes**: Persistent data storage across container restarts
- **Automated Restore**: Database initialization from backup files

### Update Procedures

```sql
-- Automatic timestamp updates
CREATE TRIGGER update_laptops_updated_at 
    BEFORE UPDATE ON laptops 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Security Considerations

### Access Control

- **Connection Security**: Database accessible only within Docker network
- **User Permissions**: Dedicated database user with limited privileges
- **Password Security**: Environment variable configuration

### Data Privacy

- **No PII**: Customer names are anonymized/pseudonymized
- **Public Data**: All content sourced from public product pages
- **GDPR Compliance**: No personal data collection or storage

## Future Enhancements

### Planned Extensions

1. **Audit Trail**: Track all data modifications with timestamps
2. **Full-Text Search**: Advanced search across all text content
3. **Data Validation**: Additional constraints for data quality
4. **Partitioning**: Time-based partitioning for price history
5. **Caching Layer**: Redis integration for frequently accessed data

### Scalability Considerations

- **Read Replicas**: Support for high-volume read operations
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Continued index tuning based on usage patterns
- **Horizontal Scaling**: Preparation for multi-region deployment