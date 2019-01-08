USE GAP_AnalyticDB;
GO

/*
SQL Query for SPP Gap Status By Huc
Used in Species Rarity Analysis

Specifically written to mimic the original XLS work 
done by Anne Davidson and Leah Dunn

Output is qtblRarityXLS dB table

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
    IF OBJECT_ID('dbo.qtblRarityXLS', 'U') IS NOT NULL 
      DROP TABLE dbo.qtblRarityXLS; 

    -- reassign all huc12/ecoL2 polygons to a single ecoL2 category
	-- drop hucs that have < 50% within ecoL2 polygon (water)
    WITH 
    -- add column identifying null ecoL2 polygons, sum count of huc12/ecoL2 combinations
    polySum AS (        
        SELECT hucs.huc12rng, 
               eco_l4.na_l2code,
			   CASE 
			    WHEN (eco_l4.na_l2code IS NULL) THEN 0 ELSE 1
			   END AS NNN,
               SUM(lu_boundary.count) AS cntTotal
        FROM lu_boundary 
             INNER JOIN hucs
              ON lu_boundary.hucs = hucs.objectid
             LEFT JOIN eco_l4
              ON lu_boundary.eco_l4 = eco_l4.fid
        --WHERE hucs.huc12rng like '030902%'
        GROUP BY hucs.huc12rng, 
                 eco_l4.na_l2code),

    -- sum based on huc/NNN 
    polyNNN AS (
        SELECT huc12rng,
		       NNN,
			   SUM(cntTotal) AS cntTotalNNN
        FROM   polySum
		GROUP BY huc12rng, NNN),

    -- find max NNN for each huc in polyNNN
    polyNNNMaxes AS (
        SELECT pNNN.*
        FROM   polyNNN pNNN
        INNER JOIN
            (SELECT huc12rng, MAX(cntTotalNNN) AS maxCntTotalNNN
             FROM polyNNN
             GROUP BY huc12rng) groupedNNNp
        ON pNNN.huc12rng = groupedNNNp.huc12rng AND
           pNNN.cntTotalNNN = groupedNNNp.maxCntTotalNNN),

	-- create list of hucs to keep
	keepHucs AS (
	    SELECT huc12rng
		FROM polyNNNMaxes
		WHERE NNN = 1),

    -- subset keepHucs from polySum
	polySum2 AS (
	    SELECT pS.huc12rng,
		       pS.na_l2code,
			   cntTotal
		FROM keepHucs kH
		INNER JOIN polySum pS
		ON kH.huc12rng = pS.huc12rng),
	
	-- find max nonNull for each huc in polySum2
	polyMaxes AS (
        SELECT pS2.*
        FROM   polySum2 pS2
        INNER JOIN
            (SELECT huc12rng, MAX(cntTotal) AS maxCntTotal
             FROM polySum2
			 WHERE na_l2code IS NOT NULL
             GROUP BY huc12rng) groupedl2p
        ON pS2.huc12rng = groupedl2p.huc12rng AND
           pS2.cntTotal = groupedl2p.maxCntTotal)

	-- deal with ties, store as temp table
    SELECT pM.huc12rng, 
           pM.na_l2code            
    INTO #polyMax
    FROM  (SELECT polyMaxes.huc12rng, 
                  polyMaxes.na_l2code,
                  ROW_NUMBER() OVER
                   (PARTITION BY polyMaxes.huc12rng 
                    ORDER BY polyMaxes.cntTotal DESC, 
                  polyMaxes.na_l2code ASC ) AS RowN
           FROM polyMaxes) pM  
    WHERE RowN = 1;                        --  81,748 records

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
         LEFT JOIN eco_l4
          ON lu_boundary.eco_l4 = eco_l4.fid;   -- 1,522,589 records

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
             lu_boundary_species.species_cd;    -- 267,849,366 records

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
             sppTotal.species_cd = sppPad3.species_cd;  -- 21,343,783 records    

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
    INTO qtblRarityXLS
    FROM #summSpp
         INNER JOIN huc_data
          ON #summSpp.huc12rng = huc_data.huc12rng
         INNER JOIN l2_data
          ON #summSpp.na_l2code = l2_data.na_l2code
         INNER JOIN l2_names
          ON #summSpp.na_l2code = l2_names.na_l2code;  -- 21,343,783 records
    -- 00:17:16 to run on BaSIC SQL Server

------------------------------------------------------------------------
-- pull results by taxa
--select * from #dist_spp;
/*
select *
from qtblRarityXLS
where Taxa = 'A'  --  1,300,645 records

select *
from qtblRarityXLS
where Taxa = 'B'  -- 13,305,635 records

select *
from qtblRarityXLS
where Taxa = 'M'  --  4,454,618 records

select *
from qtblRarityXLS
where Taxa = 'R'  --  2,282,885 records
*/

