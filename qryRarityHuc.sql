USE GAP_AnalyticDB;
GO

/*
qryRarity.sql
SQL Query for SPP Gap Status By Huc

Summarizes Gap_AnalyticDB data for species rarity analysis.
Summary by Species, HUC12/L2ecorgion, and GAP Status.
Utilizes all Huc12 polygons. L2 Ecoregion label is applied
 when missing (where Huc12 did not intersect any L2 polygon.
No hucs are discarded.
 
Output is qtblRarityHuc dB table

Steve Williams
17dec18
*/
--__________________________________________________________________________________________________________________
-- qryRarity.sql
-- drop the temp tables if they exist
IF OBJECT_ID('tempdb.dbo.#polyMax', 'U') IS NOT NULL 
  DROP TABLE tempdb.dbo.#polyMax; 
IF OBJECT_ID('tempdb.dbo.#polyData', 'U') IS NOT NULL 
  DROP TABLE tempdb.dbo.#polyData; 
IF OBJECT_ID('tempdb.dbo.#distSpp', 'U') IS NOT NULL 
  DROP TABLE tempdb.dbo.#distSpp; 
IF OBJECT_ID('tempdb.dbo.#summSpp', 'U') IS NOT NULL 
  DROP TABLE tempdb.dbo.#summSpp; 
-- drop the output table if it exists
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'qtblRarityHuc' AND TABLE_SCHEMA = 'dbo')
  DROP TABLE dbo.qtblRarityHuc;

-- reassign all huc12 polygons to a single ecoL2 category
WITH 
-- limit poly selection to hucs, sum count of huc12/ecoL2 combinations
polySum AS (        
    SELECT hucs.huc12rng, 
           eco_l4.na_l2code,
           SUM(lu_boundary.count) AS cntTotal
    FROM lu_boundary 
         INNER JOIN hucs
          ON lu_boundary.hucs = hucs.objectid
         FULL OUTER JOIN eco_l4
          ON lu_boundary.eco_l4 = eco_l4.fid
    --WHERE hucs.huc12rng like '02070011%'
    GROUP BY hucs.huc12rng, 
             eco_l4.na_l2code),  -- 96,133 records

-- create Huc List
hucList AS (
    SELECT DISTINCT huc12rng
	FROM hucs),

-- exclude NULLS
polyNotNull AS (
    SELECT *
    FROM   polySum
    WHERE  na_l2code <> 'NULL'),  -- 93,342 records

-- exclude NULLS and find max count of huc12/ecoL2 combinations
polyMaxes AS (
    SELECT pNN.*
    FROM   polyNotNull pNN
    INNER JOIN
        (SELECT huc12rng, MAX(cntTotal) AS maxCntTotal
         FROM polyNotNull
         GROUP BY huc12rng) groupedl2p
    ON pNN.huc12rng = groupedl2p.huc12rng AND
       pNN.cntTotal = groupedl2p.maxCntTotal),  -- 82,701 records

-- deal with ties
polyMax0 AS (
SELECT pM.huc12rng, 
       pM.na_l2code            
FROM  (SELECT polyMaxes.huc12rng, 
              polyMaxes.na_l2code,
              ROW_NUMBER() OVER
               (PARTITION BY polyMaxes.huc12rng 
                ORDER BY polyMaxes.cntTotal DESC, 
              polyMaxes.na_l2code ASC ) AS RowN
       FROM polyMaxes) pM  
WHERE RowN = 1)                        --  82,700 records

-- join in 17 Hucs that have no ecoregional info, save as tmp file
SELECT hL.huc12rng,
       pM.na_l2code
INTO #polyMax
FROM polyMax0 pM
	 FULL OUTER JOIN hucList hL
	  ON hL.huc12rng = pM.huc12rng;

-- set NULL ecoregions to 8.5
UPDATE pM
SET pM.na_l2code = 8.5
FROM #polyMax pM
WHERE pM.na_l2code IS NULL;

-- huc/ecoregion count data, save as temp table
SELECT lu_boundary.value AS bndValue, 
       hucs.huc12rng, 
       lu_boundary.padus1_4, 
       #polyMax.na_l2code,
       lu_boundary.count AS bndCnt
INTO #polyData
FROM #polyMax
     INNER JOIN hucs
      ON #polyMax.huc12rng = hucs.huc12rng
     INNER JOIN lu_boundary 
      ON hucs.objectid = lu_boundary.hucs
     FULL OUTER JOIN eco_l4
      ON lu_boundary.eco_l4 = eco_l4.fid;   -- 1,556,807 records

-- attach species distribution info, store as temp table
SELECT 
    #polyData.bndValue, 
    #polyData.huc12rng,
    #polyData.padus1_4,
    #polyData.na_l2code,
    lu_boundary_species.species_cd,
    SUM(lu_boundary_species.count) AS bndsppCnt
INTO #distSpp
FROM #polyData 
     INNER JOIN lu_boundary_species
      ON #polyData.bndValue = lu_boundary_species.boundary
GROUP BY #polyData.bndValue, 
         #polyData.huc12rng,
         #polyData.padus1_4,
         #polyData.na_l2code,
         lu_boundary_species.species_cd;    -- 273,686,225 records

-- generate table of total species distribution count per huc
WITH
sppTotal AS (
    SELECT dist_spp_0.huc12rng, 
           dist_spp_0.species_cd,
           dist_spp_0.na_l2code,
           SUM(dist_spp_0.bndSppCnt) AS totalSppPix
    FROM #distSpp AS dist_spp_0 
         LEFT JOIN padus1_4 AS padus1_4_0
          ON dist_spp_0.padus1_4 = padus1_4_0.objectid
    GROUP BY dist_spp_0.huc12rng, 
             dist_spp_0.species_cd,
             dist_spp_0.na_l2code),   

-- generate table of gap status 1 species distribution count per huc
sppPad1 AS (
    SELECT dist_spp_1.huc12rng, 
           dist_spp_1.species_cd,
           SUM(dist_spp_1.bndsppCnt) AS gs1SppPix
    FROM #distSpp AS dist_spp_1 
         LEFT JOIN padus1_4 AS padus1_4_1 
          ON dist_spp_1.padus1_4 = padus1_4_1.objectid
    WHERE (RTRIM(LTRIM(padus1_4_1.gap_sts)) = '1')
    GROUP BY dist_spp_1.huc12rng, 
             dist_spp_1.species_cd),
    
-- generate table of gap status 2 species distribution count per huc
sppPad2 AS (
    SELECT dist_spp_2.huc12rng, 
           dist_spp_2.species_cd,
           SUM(dist_spp_2.bndsppCnt) AS gs2SppPix
    FROM #distSpp AS dist_spp_2 
         LEFT JOIN padus1_4 AS padus1_4_2 
          ON dist_spp_2.padus1_4 = padus1_4_2.objectid
    WHERE (RTRIM(LTRIM(padus1_4_2.gap_sts)) = '2')
    GROUP BY dist_spp_2.huc12rng, 
             dist_spp_2.species_cd), 
             
-- generate table of gap status 3 species distribution count per huc
sppPad3 AS (
    SELECT dist_spp_3.huc12rng, 
           dist_spp_3.species_cd,
           SUM(dist_spp_3.bndsppCnt) AS gs3SppPix
    FROM #distSpp AS dist_spp_3 
         LEFT JOIN padus1_4 AS padus1_4_3 
          ON dist_spp_3.padus1_4 = padus1_4_3.objectid
    WHERE (RTRIM(LTRIM(padus1_4_3.gap_sts)) = '3')
    GROUP BY dist_spp_3.huc12rng, 
             dist_spp_3.species_cd) 

-- combine gap status and total counts, save as temp table
SELECT sppTotal.huc12rng,
       sppTotal.na_l2code, 
       UPPER(LEFT(sppTotal.species_cd, 1)) AS Taxa, 
       LEFT(sppTotal.species_cd, 1)
        + UPPER(SUBSTRING(sppTotal.species_cd, 2, 4))
        + RIGHT(sppTotal.species_cd, 1) AS Spp, 
       ISNULL(sppPad1.gs1SppPix, 0) AS gs1SppPix, 
       ISNULL(sppPad2.gs2SppPix, 0) AS gs2SppPix, 
       ISNULL(sppPad3.gs3SppPix, 0) AS gs3SppPix, 
       totalSppPix - (ISNULL(sppPad1.gs1SppPix, 0) + 
                      ISNULL(sppPad2.gs2SppPix, 0) + 
                      ISNULL(sppPad3.gs3SppPix, 0)) AS gs4SppPix, 
       sppTotal.totalSppPix
INTO #summSpp
FROM sppTotal 
     LEFT OUTER JOIN sppPad1
      ON sppTotal.huc12rng = sppPad1.huc12rng AND 
         sppTotal.species_cd = sppPad1.species_cd
     LEFT OUTER JOIN sppPad2
      ON sppTotal.huc12rng = sppPad2.huc12rng AND
         sppTotal.species_cd = sppPad2.species_cd
     LEFT OUTER JOIN sppPad3 
      ON sppTotal.huc12rng = sppPad3.huc12rng AND 
         sppTotal.species_cd = sppPad3.species_cd;  -- 21,613,984 records    

-- combine summSpp, huc and l2 info, save as output table
WITH
-- caluclate pixel count for each huc
huc_data AS (
    SELECT huc12rng,
           SUM(bndCnt) AS hucPix
    FROM #polyData
    GROUP BY huc12rng),    

-- calculate pixel count for each redefined L2 ecoregion
l2_data AS (
    SELECT na_l2code,
           SUM(bndCnt) AS ecoPix
    FROM #polyData
    GROUP BY na_l2code),

-- generate table of l2 ecoregion names
l2_names AS (
    SELECT DISTINCT
        na_l2code,
        REPLACE(na_l2name,' (?)','') AS na_l2name
    FROM eco_l4)

SELECT #summSpp.huc12rng,
       huc_data.hucPix,
       #summSpp.na_l2code,
       l2_names.na_l2name,
       l2_data.ecoPix,
       #summSpp.Taxa,
       #summSpp.Spp,
       #summSpp.gs1SppPix,
       #summSpp.gs2SppPix,
       #summSpp.gs3SppPix,
       #summSpp.gs4SppPix,
       #summSpp.totalSppPix
INTO qtblRarityHuc
FROM #summSpp
     INNER JOIN huc_data
      ON #summSpp.huc12rng = huc_data.huc12rng
     INNER JOIN l2_data
      ON #summSpp.na_l2code = l2_data.na_l2code
     INNER JOIN l2_names
      ON #summSpp.na_l2code = l2_names.na_l2code;  -- 21,613,984 records
-- 00:25:27 to run on BaSIC SQL Server

------------------------------------------------------------------------
-- pull results by taxa
--select * from #dist_spp;
/*
select *
from qtblRarityHuc
where Taxa = 'A'  --  1,316,399 records

select *
from qtblRarityHuc
where Taxa = 'B'  -- 13,492,552 records

select *
from qtblRarityHuc
where Taxa = 'M'  --  4,496,460 records

select *
from qtblRarityHuc
where Taxa = 'R'  --  2,307,149 records
*/