CREATE TABLE IF NOT EXISTS metro (
    id BIGINT PRIMARY KEY UNIQUE,
    name VARCHAR(40),
    bandwidth FLOAT
);

CREATE TABLE IF NOT EXISTS flow_metro (
    id SERIAL PRIMARY KEY,
    metro_id BIGINT,
    time TIME,
    flow FLOAT,
    FOREIGN KEY (metro_id) REFERENCES metro(id)
);


CREATE TABLE IF NOT EXISTS ways (
    id BIGINT PRIMARY KEY UNIQUE,
    bandwidth FLOAT
);

CREATE TABLE IF NOT EXISTS flow_ways (
    id SERIAL PRIMARY KEY,
    ways_id BIGINT,
    time TIME,
    flow FLOAT,
    FOREIGN KEY (ways_id) REFERENCES ways(id)
);


