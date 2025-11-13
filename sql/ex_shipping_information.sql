CREATE TABLE ex_shipping_information
(
    uuid               CHAR(36)      DEFAULT (UUID()) NOT NULL,
    img_parse_url      TEXT,
    detail_url         TEXT,
    detail_title       TEXT,
    detail_date        DATE,
    detail_timestamptz VARCHAR(30),
    detail_contents    TEXT,
    article_id         VARCHAR(50)  NOT NULL          NOT NULL,
    update_time        TIMESTAMP,
    class_level_1      VARCHAR(100),
    class_level_2      VARCHAR(100),
    keyword1           VARCHAR(100),
    keyword2           VARCHAR(100),
    keyword3           VARCHAR(100),
    is_translated      VARCHAR(10)   DEFAULT 'no'     NOT NULL,
    abstract           TEXT,
    detail_title_cn    TEXT,
    detail_contents_cn TEXT,
    abstract_cn        TEXT,
    PRIMARY KEY (article_id)
);

CREATE INDEX idx_article_id ON ex_shipping_information (article_id);