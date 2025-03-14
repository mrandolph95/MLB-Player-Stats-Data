CREATE DATABASE mlb_data;

SELECT *
FROM "LA_Dodgers_Box_Scores"
LIMIT 5;


# Calculate stats
SELECT 
    "Player ID",
    "Name",
    CASE 
        WHEN SUM("At Bats") = 0 THEN 0
        ELSE SUM("Hits") / SUM("At Bats")
    END AS Batting_Avg,
    CASE 
        WHEN (SUM("At Bats") + SUM("Walks")) = 0 THEN 0
        ELSE (SUM("Hits") + SUM("Walks")) / (SUM("At Bats") + SUM("Walks"))
    END AS OBP,
    CASE 
        WHEN SUM("At Bats") = 0 THEN 0
        ELSE ((1 * SUM("Hits")) + (2 * SUM("Doubles")) + (3 * SUM("Triples")) + (4 * SUM("Home Runs"))) / SUM("At Bats")
    END AS SLG,
    CASE 
        WHEN (SUM("At Bats") + SUM("Walks")) = 0 THEN 0
        ELSE (SUM("Hits") + SUM("Walks")) / (SUM("At Bats") + SUM("Walks")) + ((1 * SUM("Hits")) + (2 * SUM("Doubles")) + (3 * SUM("Triples")) + (4 * SUM("Home Runs"))) / SUM("At Bats")
    END AS OPS,
    CASE 
        WHEN COUNT(DISTINCT "Game ID") = 0 THEN 0
        ELSE SUM("RBI") / COUNT(DISTINCT "Game ID")
    END AS RBI_per_game,
    CASE 
        WHEN SUM("Walks") = 0 THEN 0
        ELSE SUM("Strikeouts") / SUM("Walks")
    END AS K_BB_Ratio,
    CASE 
        WHEN SUM("Innings Pitched") = 0 THEN 0
        ELSE (SUM("Earned Runs") / SUM("Innings Pitched")) * 9
    END AS ERA,
    CASE
        WHEN SUM("Innings Pitched") = 0 THEN 0
        ELSE (SUM("Walks") + SUM("Hits")) / SUM("Innings Pitched")
    END AS WHIP,
    CASE 
        WHEN SUM("Innings Pitched") = 0 THEN 0
        ELSE (SUM("Pitching Strikeouts") / SUM("Innings Pitched")) * 9
    END AS K_9
FROM 
    "LA_Dodgers_Box_Scores"
GROUP BY 
    "Player ID", "Name";


--Player rank

SELECT 
    "Player ID",
    "Name",
    SUM("Hits") / NULLIF(SUM("At Bats"), 0) AS Batting_Avg,
    RANK() OVER (PARTITION BY "Game ID" ORDER BY SUM("Hits") / NULLIF(SUM("At Bats"), 0) DESC) AS Rank
FROM 
    "LA_Dodgers_Box_Scores"
GROUP BY 
    "Player ID", "Name", "Game ID"
ORDER BY 
    "Game ID", Rank;

--Top 3 players by RBI

SELECT 
    "Player ID",
    "Name",
    SUM(RBI) AS Total_RBI,
    RANK() OVER (ORDER BY SUM(RBI) DESC) AS Rank
FROM 
    "LA_Dodgers_Box_Scores"
GROUP BY 
    "Player ID", "Name"
HAVING 
    RANK() <= 3
ORDER BY 
    Rank;

--Total home runs per MONTH

SELECT 
    "Player ID",
    "Name",
    EXTRACT(MONTH FROM "Game Date") AS Month,
    EXTRACT(YEAR FROM "Game Date") AS Year,
    SUM("Home Runs") AS Total_Home_Runs
FROM 
    "LA_Dodgers_Box_Scores"
GROUP BY 
    "Player ID", "Name", Month, Year
ORDER BY 
    Year, Month, Total_Home_Runs DESC;






