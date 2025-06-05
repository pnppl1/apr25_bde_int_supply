-- Trustpilot Data Database Schema

-- Drop tables if they exist (in reverse order due to foreign key constraints)
DROP TABLE IF EXISTS company_domain CASCADE;
DROP TABLE IF EXISTS review CASCADE;
DROP TABLE IF EXISTS rating CASCADE;
DROP TABLE IF EXISTS domain CASCADE;
DROP TABLE IF EXISTS company CASCADE;

-- Create Company table
CREATE TABLE company (
    website VARCHAR(255) PRIMARY KEY,
    company VARCHAR(255) NOT NULL,
    trust_score DECIMAL(3,2),
    number_review INTEGER 
);

-- Create Domain table
CREATE TABLE domain (
    domain_id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL UNIQUE
);

-- Create Rating table (star percentages for each company)
CREATE TABLE rating (
    website VARCHAR(255) PRIMARY KEY,
    -- star_5_percentage DECIMAL(5,2),
    -- star_4_percentage DECIMAL(5,2),
    -- star_3_percentage DECIMAL(5,2),
    -- star_2_percentage DECIMAL(5,2),
    -- star_1_percentage DECIMAL(5,2),
    "5_star_percentage" TEXT,
    "4_star_percentage" TEXT,
    "3_star_percentage" TEXT,
    "2_star_percentage" TEXT,
    "1_star_percentage" TEXT,
    FOREIGN KEY (website) REFERENCES company(website) ON DELETE CASCADE
);

-- Create Review table
CREATE TABLE review (
    website VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    country VARCHAR(100),
    rating INTEGER,
    title TEXT,
    text TEXT,
    date_of_experience DATE,
    has_reply BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (website) REFERENCES company(website) ON DELETE CASCADE
);

-- Create Company_Domain junction table (Many-to-Many relationship)
CREATE TABLE company_domain (
    website VARCHAR(255),
    domain_id INTEGER,
    PRIMARY KEY (website, domain_id),
    FOREIGN KEY (website) REFERENCES company(website) ON DELETE CASCADE,
    FOREIGN KEY (domain_id) REFERENCES domain(domain_id) ON DELETE CASCADE
);


-- comments for documentation
COMMENT ON TABLE company IS 'Stores company information including website, name, trust score and review count';
COMMENT ON TABLE domain IS 'Stores unique domain/industry categories';
COMMENT ON TABLE rating IS 'Stores percentage distribution of star ratings for each company';
COMMENT ON TABLE review IS 'Stores individual reviews with reviewer information and content';
COMMENT ON TABLE company_domain IS 'Junction table linking companies to their operating domains/industries';

COMMENT ON COLUMN company.website IS 'Company website URL - serves as primary key';
COMMENT ON COLUMN company.trust_score IS 'Trust score of the company (0.00 to 5.00)';
COMMENT ON COLUMN company.number_review IS 'Total number of reviews for this company';
COMMENT ON COLUMN review.rating IS 'Star rating given by reviewer (1-5)';
COMMENT ON COLUMN review.has_reply IS 'Whether the company replied to this review';
