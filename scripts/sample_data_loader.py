"""
Sample data loader script - loads high-quality sample data for price_snapshots, reviews, and questions_answers tables.
Preserves laptop and specification data.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.src.app.core.db import SessionLocal
from backend.src.app.models.laptop import Laptop
from backend.src.app.models.specification import Specification
from backend.src.app.models.price_snapshot import PriceSnapshot
from backend.src.app.models.review import Review
from backend.src.app.models.questions_answer import QuestionsAnswer
from backend.src.utils.logger.logging import logger as logging


def load_sample_data():
    """Load comprehensive sample data for demonstration purposes."""
    db = SessionLocal()

    try:
        logging.info("Starting sample data load...")
        logging.info("=" * 60)

        # Load price snapshots
        price_snapshots_sql = """
-- Lenovo ThinkPad E14 Gen 5 (Intel) - laptop_id = 1
INSERT INTO price_snapshots (laptop_id, price, currency, availability_status, shipping_info, promotion_text, configuration_summary, scraped_at) VALUES
(1, 1019.00, 'USD', 'In Stock', 'Free shipping, 3-5 business days', NULL, 'Core i5-1335U / 8GB RAM / 256GB SSD', NOW() - INTERVAL '1 day'),
(1, 1024.99, 'USD', 'In Stock', 'Free shipping, 3-5 business days', NULL, 'Core i5-1335U / 8GB RAM / 256GB SSD', NOW() - INTERVAL '3 days'),
(1, 999.99, 'USD', 'In Stock', 'Free shipping, 3-5 business days', '2% off limited time', 'Core i5-1335U / 8GB RAM / 256GB SSD', NOW() - INTERVAL '7 days'),
(1, 1149.00, 'USD', 'In Stock', 'Free shipping, 3-5 business days', NULL, 'Core i7-1355U / 16GB RAM / 512GB SSD', NOW() - INTERVAL '1 day'),
(1, 1159.99, 'USD', 'Limited Stock', 'Free shipping, 5-7 business days', NULL, 'Core i7-1355U / 16GB RAM / 512GB SSD', NOW() - INTERVAL '5 days'),
(1, 1299.00, 'USD', 'In Stock', 'Free shipping, 3-5 business days', NULL, 'Core i7-1360P / 16GB RAM / 1TB SSD', NOW() - INTERVAL '2 days'),

-- Lenovo ThinkPad E14 Gen 5 (AMD) - laptop_id = 2
(2, 899.00, 'USD', 'In Stock', 'Free shipping, 3-5 business days', NULL, 'Ryzen 5 7430U / 8GB RAM / 256GB SSD', NOW() - INTERVAL '1 day'),
(2, 919.99, 'USD', 'In Stock', 'Free shipping, 3-5 business days', NULL, 'Ryzen 5 7430U / 8GB RAM / 256GB SSD', NOW() - INTERVAL '4 days'),
(2, 849.99, 'USD', 'In Stock', 'Free shipping, 3-5 business days', 'Early bird special', 'Ryzen 5 7430U / 8GB RAM / 256GB SSD', NOW() - INTERVAL '10 days'),
(2, 1049.00, 'USD', 'In Stock', 'Free shipping, 3-5 business days', NULL, 'Ryzen 7 7730U / 16GB RAM / 512GB SSD', NOW() - INTERVAL '1 day'),
(2, 1079.99, 'USD', 'Limited Stock', 'Free shipping, 5-7 business days', NULL, 'Ryzen 7 7730U / 16GB RAM / 512GB SSD', NOW() - INTERVAL '6 days'),

-- HP ProBook 450 G10 - laptop_id = 3
(3, 899.99, 'USD', 'In Stock', 'Free shipping, 2-4 business days', NULL, 'Core i5-1335U / 8GB RAM / 256GB SSD', NOW() - INTERVAL '1 day'),
(3, 924.99, 'USD', 'In Stock', 'Free shipping, 2-4 business days', NULL, 'Core i5-1335U / 8GB RAM / 256GB SSD', NOW() - INTERVAL '5 days'),
(3, 879.99, 'USD', 'In Stock', 'Free shipping, 2-4 business days', 'Volume discount available', 'Core i5-1335U / 8GB RAM / 256GB SSD', NOW() - INTERVAL '8 days'),
(3, 1199.00, 'USD', 'In Stock', 'Free shipping, 2-4 business days', NULL, 'Core i7-1355U / 16GB RAM / 512GB SSD', NOW() - INTERVAL '2 days'),
(3, 1299.99, 'USD', 'Limited Stock', 'Free shipping, 4-6 business days', NULL, 'Core i7-1360P / 32GB RAM / 1TB SSD', NOW() - INTERVAL '3 days'),

-- HP ProBook 440 G11 - laptop_id = 4
(4, 749.99, 'USD', 'In Stock', 'Free shipping, 2-4 business days', NULL, 'Core Ultra 5 125U / 8GB RAM / 256GB SSD', NOW() - INTERVAL '1 day'),
(4, 769.99, 'USD', 'In Stock', 'Free shipping, 2-4 business days', NULL, 'Core Ultra 5 125U / 8GB RAM / 256GB SSD', NOW() - INTERVAL '6 days'),
(4, 719.99, 'USD', 'In Stock', 'Free shipping, 2-4 business days', 'Back to business sale', 'Core Ultra 5 125U / 8GB RAM / 256GB SSD', NOW() - INTERVAL '12 days'),
(4, 999.00, 'USD', 'In Stock', 'Free shipping, 2-4 business days', NULL, 'Core Ultra 7 155U / 16GB RAM / 512GB SSD', NOW() - INTERVAL '1 day'),
(4, 1149.99, 'USD', 'In Stock', 'Free shipping, 2-4 business days', NULL, 'Core Ultra 7 155H / 16GB RAM / 1TB SSD', NOW() - INTERVAL '4 days'),
(4, 1399.99, 'USD', 'Limited Stock', 'Free shipping, 4-6 business days', NULL, 'Core Ultra 7 155H / 32GB RAM / 1TB SSD + RTX 2050', NOW() - INTERVAL '7 days');
        """

        reviews_sql = """
-- Lenovo ThinkPad E14 Gen 5 (Intel) reviews
INSERT INTO reviews (laptop_id, rating, review_title, review_text, reviewer_name, reviewer_verified, review_date, helpful_count, configuration_summary) VALUES
(1, 5, 'Excellent business laptop', 'Been using this ThinkPad for 6 months now and it''s been rock solid. The keyboard is fantastic for long coding sessions, battery easily lasts a full workday, and the build quality feels premium. The trackpoint takes some getting used to but becomes very efficient. Highly recommend for business use.', 'TechManager_Sarah', true, NOW() - INTERVAL '14 days', 23, 'Core i5-1335U / 8GB RAM / 256GB SSD'),
(1, 4, 'Good value for enterprise deployment', 'We deployed 50 of these across our organization. Overall very satisfied - good performance for office apps, reliable, and the IT department likes the management features. Only complaint is the screen could be brighter for outdoor use. Great price point for business laptops.', 'ITDirector_Mike', true, NOW() - INTERVAL '28 days', 18, 'Core i5-1335U / 8GB RAM / 256GB SSD'),
(1, 5, 'Perfect for remote work', 'Working from home setup and this laptop handles everything I throw at it. Multiple browser tabs, video calls, Office suite - no lag. The webcam quality is decent and microphone picks up voice clearly. Ports are perfect - no dongles needed. Love the matte display.', 'RemoteWorker_Alex', true, NOW() - INTERVAL '45 days', 31, 'Core i7-1355U / 16GB RAM / 512GB SSD'),
(1, 3, 'Decent but not exceptional', 'It''s a solid business laptop but nothing that wow''s you. Performance is adequate, build quality is good but not amazing. The fan can get loud under heavy load. For the price it''s reasonable but there are probably better options out there.', 'BusinessUser123', false, NOW() - INTERVAL '67 days', 8, 'Core i5-1335U / 8GB RAM / 256GB SSD'),
(1, 4, 'Great keyboard, average everything else', 'The keyboard is definitely the highlight - very comfortable for typing. Performance is fine for business apps but can slow down with heavy multitasking. Battery life is good, usually get 7-8 hours. Build quality feels solid. Would buy again.', 'WriterPro', true, NOW() - INTERVAL '89 days', 15, 'Core i5-1335U / 8GB RAM / 256GB SSD'),
(1, 5, 'ThinkPad reliability continues', 'This is my 4th ThinkPad over the years and the quality remains consistent. Fast boot times, responsive performance, excellent security features. The spill-resistant keyboard has already saved me once. Worth every penny for business use.', 'CorpConsultant', true, NOW() - INTERVAL '112 days', 27, 'Core i7-1355U / 16GB RAM / 512GB SSD'),

-- Lenovo ThinkPad E14 Gen 5 (AMD) reviews
(2, 5, 'AMD performance exceeds expectations', 'The Ryzen processor in this ThinkPad is fantastic. Much better performance per dollar compared to Intel variants. Battery life is excellent - easily 10+ hours of office work. The integrated graphics are surprisingly capable. Highly recommend this configuration.', 'TechEnthusiast_Dave', true, NOW() - INTERVAL '21 days', 34, 'Ryzen 7 7730U / 16GB RAM / 512GB SSD'),
(2, 4, 'Great price-performance ratio', 'Chose the AMD version for better value and haven''t been disappointed. Handles all my business applications smoothly, multitasking is great with 16GB RAM. The trackpoint is handy once you get used to it. Minor complaint about fan noise but overall very satisfied.', 'StartupFounder_Jane', true, NOW() - INTERVAL '38 days', 19, 'Ryzen 7 7730U / 16GB RAM / 512GB SSD'),
(2, 4, 'Solid for accounting work', 'Using this for accounting and financial modeling. Runs Excel with large datasets without issues, QuickBooks works perfectly. The number pad layout takes some adjustment but manageable. Good value for the performance you get.', 'AccountantPro', true, NOW() - INTERVAL '56 days', 12, 'Ryzen 5 7430U / 8GB RAM / 256GB SSD'),
(2, 5, 'Best business laptop I''ve owned', 'Upgraded from an older laptop and the difference is night and day. The AMD chip handles everything I need - development tools, VMs, multiple IDEs. Battery life is impressive and the screen quality is good. ThinkPad build quality as expected.', 'DevManager_Tom', true, NOW() - INTERVAL '74 days', 28, 'Ryzen 7 7730U / 16GB RAM / 512GB SSD'),
(2, 3, 'Good but screen could be better', 'Performance is solid and the laptop feels well-built. My main issue is with the display - colors seem washed out and brightness isn''t great. Fine for office work but disappointing for presentations. Everything else is good though.', 'SalesManager_Lisa', false, NOW() - INTERVAL '95 days', 9, 'Ryzen 5 7430U / 8GB RAM / 256GB SSD'),

-- HP ProBook 450 G10 reviews
(3, 4, 'Reliable workhorse for business', 'Been using this HP ProBook for 8 months in a corporate environment. It''s been very reliable, handles all standard business applications well. The larger 15.6" screen is nice for productivity. Good port selection means no dongles needed. Recommended for office use.', 'CorpUser_Mark', true, NOW() - INTERVAL '32 days', 22, 'Core i5-1335U / 8GB RAM / 256GB SSD'),
(3, 5, 'Great value for money', 'Fantastic laptop for the price point. Performance is smooth for all my needs - spreadsheets, presentations, web browsing. Battery easily lasts a full day. The build quality feels premium without the premium price. Very happy with this purchase.', 'SmallBizOwner', true, NOW() - INTERVAL '47 days', 31, 'Core i7-1355U / 16GB RAM / 512GB SSD'),
(3, 4, 'Good for travel and presentations', 'As a sales consultant who travels frequently, this laptop has been great. Not too heavy, good screen for client presentations, and reliable performance. The HP security features work well with our corporate policies. Would recommend for business travelers.', 'SalesConsultant_Amy', true, NOW() - INTERVAL '63 days', 16, 'Core i5-1335U / 8GB RAM / 256GB SSD'),
(3, 3, 'Average performance, good build', 'It''s a decent laptop but nothing extraordinary. Performance is adequate for basic tasks but can slow down with heavy multitasking. Build quality is solid though and it feels durable. For the price, it''s acceptable but not impressive.', 'OfficeWorker_Jim', false, NOW() - INTERVAL '81 days', 7, 'Core i5-1335U / 8GB RAM / 256GB SSD'),
(3, 4, 'Solid choice for education sector', 'We bought several of these for our training department. They handle educational software well, are durable enough for classroom use, and the IT team likes the manageability features. Good balance of features and cost for institutional use.', 'EduTech_Coordinator', true, NOW() - INTERVAL '102 days', 14, 'Core i5-1335U / 8GB RAM / 256GB SSD'),

-- HP ProBook 440 G11 reviews
(4, 5, 'Intel Core Ultra is impressive', 'The new Core Ultra processor in this ProBook is noticeably faster than previous generations. Great for business applications and the AI features are starting to show benefits. Compact 14" form factor is perfect for portability without sacrificing performance.', 'TechReviewer_Sarah', true, NOW() - INTERVAL '18 days', 29, 'Core Ultra 7 155U / 16GB RAM / 512GB SSD'),
(4, 4, 'Perfect size for business travel', 'The 14" form factor hits the sweet spot between portability and usability. Fits easily in my briefcase, lightweight for travel, but screen is large enough for productive work. Performance handles all my business needs. Battery life is solid for a full day.', 'BusinessTraveler_John', true, NOW() - INTERVAL '35 days', 21, 'Core Ultra 5 125U / 8GB RAM / 256GB SSD'),
(4, 4, 'Great for hybrid work setup', 'Using this for hybrid work - office and home setup. The port selection is excellent for connecting to various monitors and peripherals. Performance is snappy, build quality feels premium. The HP Wolf security features integrate well with our corporate setup.', 'HybridWorker_Maria', true, NOW() - INTERVAL '52 days', 18, 'Core Ultra 7 155U / 16GB RAM / 512GB SSD'),
(4, 5, 'Excellent for development work', 'As a software developer, this laptop handles my workflow perfectly. The Core Ultra processor makes compilation noticeably faster. 16GB RAM handles multiple IDEs and containers without issue. The keyboard is comfortable for long coding sessions.', 'Developer_Chris', true, NOW() - INTERVAL '69 days', 33, 'Core Ultra 7 155H / 16GB RAM / 1TB SSD'),
(4, 3, 'Good but expensive for what you get', 'It''s a solid laptop with good performance and build quality. However, I feel it''s slightly overpriced compared to similar spec laptops from other brands. The HP brand premium is noticeable. Performance and features are good though.', 'BudgetConscious_User', false, NOW() - INTERVAL '87 days', 11, 'Core Ultra 5 125U / 8GB RAM / 256GB SSD'),
(4, 4, 'Reliable for financial work', 'Using this for financial analysis and modeling. The processor handles complex Excel workbooks and financial software without issues. Screen quality is good for long work sessions. The security features give me confidence for sensitive financial data.', 'FinanceAnalyst_Robert', true, NOW() - INTERVAL '104 days', 16, 'Core Ultra 7 155U / 16GB RAM / 512GB SSD');
        """

        qa_sql = """
-- Questions and Answers
INSERT INTO questions_answers (laptop_id, question_text, answer_text, asker_name, answerer_name, question_date, answer_date, helpful_count, configuration_summary) VALUES
-- Lenovo ThinkPad E14 Gen 5 (Intel)
(1, 'Can this laptop handle video editing for business presentations?', 'Yes, it handles basic video editing well. I use it for creating training videos and marketing content. The integrated graphics are sufficient for 1080p editing in tools like Premiere Pro or DaVinci Resolve, though render times are moderate.', 'MarketingManager_Pete', 'VideoProducer_Kate', NOW() - INTERVAL '25 days', NOW() - INTERVAL '23 days', 8, 'Core i7-1355U / 16GB RAM / 512GB SSD'),
(1, 'How is the keyboard for programming work?', 'Excellent! The ThinkPad keyboard is legendary for a reason. Great key travel, responsive, and the layout is perfect for coding. The trackpoint is also handy for precise cursor control without leaving the home row.', 'NewDeveloper_Sam', 'SeniorDev_Lisa', NOW() - INTERVAL '42 days', NOW() - INTERVAL '40 days', 15, 'Core i5-1335U / 8GB RAM / 256GB SSD'),
(1, 'Is 8GB RAM enough for business use?', '8GB is adequate for basic business tasks, but I''d recommend 16GB if you do heavy multitasking or run VMs. The good news is this model supports up to 40GB so you can upgrade later.', 'ProcurementManager', 'ITAdmin_Jake', NOW() - INTERVAL '58 days', NOW() - INTERVAL '56 days', 12, 'Core i5-1335U / 8GB RAM / 256GB SSD'),
(1, 'How does it compare to the AMD version?', 'Both are great. Intel version has slightly better single-core performance and Thunderbolt support. AMD version offers better battery life and integrated graphics. Choose based on your priorities.', 'TechBuyer_Anna', 'LaptopExpert_Mike', NOW() - INTERVAL '73 days', NOW() - INTERVAL '71 days', 19, 'Core i5-1335U / 8GB RAM / 256GB SSD'),

-- Lenovo ThinkPad E14 Gen 5 (AMD)
(2, 'How is gaming performance on this laptop?', 'Not designed for gaming, but the AMD integrated graphics can handle light gaming and older titles at low-medium settings. Fine for casual games during breaks, but don''t expect AAA gaming performance.', 'OfficeGamer_Tom', 'TechReviewer_Sarah', NOW() - INTERVAL '33 days', NOW() - INTERVAL '31 days', 6, 'Ryzen 7 7730U / 16GB RAM / 512GB SSD'),
(2, 'Can I connect three external monitors?', 'Yes, with the USB-C ports supporting DisplayPort you can run dual external monitors plus the laptop screen. For three external monitors, you might need a docking station.', 'MultiMonitor_User', 'ITSupport_David', NOW() - INTERVAL '49 days', NOW() - INTERVAL '47 days', 11, 'Ryzen 5 7430U / 8GB RAM / 256GB SSD'),
(2, 'Battery life for all-day meetings?', 'Absolutely. I regularly get 10-12 hours with typical office work and video calls. The AMD processor is very power efficient. Perfect for long conference days without hunting for outlets.', 'ExecutiveAssistant', 'FrequentFlyer_Mark', NOW() - INTERVAL '65 days', NOW() - INTERVAL '63 days', 17, 'Ryzen 7 7730U / 16GB RAM / 512GB SSD'),

-- HP ProBook 450 G10
(3, 'Is the 15.6" screen too big for travel?', 'It''s definitely larger than ultrabooks, but still manageable for travel. I take mine on business trips regularly. The extra screen real estate is worth it for productivity. Fits in most laptop bags without issue.', 'BusinessTraveler_Jane', 'RoadWarrior_Bob', NOW() - INTERVAL '27 days', NOW() - INTERVAL '25 days', 9, 'Core i5-1335U / 8GB RAM / 256GB SSD'),
(3, 'How does HP support compare to Lenovo?', 'HP business support has been solid in my experience. Response times are good and they understand enterprise needs. Both HP and Lenovo have good business support - comes down to personal preference.', 'ITManager_Susan', 'TechProcurement_Al', NOW() - INTERVAL '44 days', NOW() - INTERVAL '42 days', 13, 'Core i7-1355U / 16GB RAM / 512GB SSD'),
(3, 'Can this run CAD software?', 'For light CAD work, yes. I use it for AutoCAD 2D and basic 3D modeling. The integrated graphics handle simple models fine, but for heavy 3D work you''d want a laptop with dedicated graphics.', 'Engineer_Carlos', 'CAD_Specialist_Amy', NOW() - INTERVAL '61 days', NOW() - INTERVAL '59 days', 7, 'Core i7-1355U / 16GB RAM / 512GB SSD'),

-- HP ProBook 440 G11
(4, 'What are the AI features in Core Ultra?', 'The Core Ultra has a dedicated NPU (Neural Processing Unit) for AI workloads. Currently used for things like Windows Studio Effects, background blur in video calls, and some productivity features. More AI apps coming.', 'TechCurious_Pat', 'AIEnthusiast_Jordan', NOW() - INTERVAL '19 days', NOW() - INTERVAL '17 days', 14, 'Core Ultra 7 155U / 16GB RAM / 512GB SSD'),
(4, 'How does build quality compare to ThinkPad?', 'Both are well-built business laptops. ThinkPad has a more utilitarian design and the famous keyboard. HP ProBook is more modern looking with good build quality. Both are reliable for business use.', 'LaptopShopper_Ben', 'BusinessUser_Carol', NOW() - INTERVAL '36 days', NOW() - INTERVAL '34 days', 16, 'Core Ultra 5 125U / 8GB RAM / 256GB SSD'),
(4, 'Is the RTX 2050 worth the upgrade?', 'If you do any graphics work, light gaming, or 3D modeling, yes. For pure business use, the integrated graphics are sufficient. The RTX 2050 adds capability but also cost and reduced battery life.', 'GraphicsUser_Maya', 'TechAdvisor_Steve', NOW() - INTERVAL '53 days', NOW() - INTERVAL '51 days', 10, 'Core Ultra 7 155H / 16GB RAM / 1TB SSD + RTX 2050'),
(4, 'Recommended for data science work?', 'The Core Ultra performs well for data analysis and machine learning. 16GB RAM is adequate for medium datasets. The NPU can accelerate some AI workloads. For heavy ML training, you''d want more RAM and possibly discrete GPU.', 'DataScientist_Raj', 'MLEngineer_Emma', NOW() - INTERVAL '70 days', NOW() - INTERVAL '68 days', 18, 'Core Ultra 7 155U / 16GB RAM / 512GB SSD');
        """

        # Execute the SQL statements
        logging.info("Loading price snapshots...")
        db.execute(text(price_snapshots_sql))

        logging.info("Loading reviews...")
        db.execute(text(reviews_sql))

        logging.info("Loading Q&A data...")
        db.execute(text(qa_sql))

        # Commit all changes
        db.commit()

        # Verify data was loaded
        price_count = db.query(PriceSnapshot).count()
        review_count = db.query(Review).count()
        qa_count = db.query(QuestionsAnswer).count()

        logging.info("Sample data loaded successfully:")
        logging.info(f"  Price snapshots: {price_count}")
        logging.info(f"  Reviews: {review_count}")
        logging.info(f"  Q&A entries: {qa_count}")
        logging.info("=" * 60)
        logging.info("Database ready for demonstration!")

    except Exception as e:
        logging.error(f"Sample data load failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_sample_data()
