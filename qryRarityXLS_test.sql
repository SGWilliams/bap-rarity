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
WHERE hucs.huc12rng = '010100010102' OR
hucs.huc12rng = '010200020302' OR
hucs.huc12rng = '010200040111' OR
hucs.huc12rng = '010200040409' OR
hucs.huc12rng = '010300030802' OR
hucs.huc12rng = '010500021308' OR
hucs.huc12rng = '010500022218' OR
hucs.huc12rng = '010802010604' OR
hucs.huc12rng = '020200020605' OR
hucs.huc12rng = '020301010404' OR
hucs.huc12rng = '020301030205' OR
hucs.huc12rng = '020301040304' OR
hucs.huc12rng = '020302020606' OR
hucs.huc12rng = '020401040303' OR
hucs.huc12rng = '020401050204' OR
hucs.huc12rng = '020401060304' OR
hucs.huc12rng = '020402030503' OR
hucs.huc12rng = '020501070201' OR
hucs.huc12rng = '020502050607' OR
hucs.huc12rng = '020503050505' OR
hucs.huc12rng = '020503050906' OR
hucs.huc12rng = '020700090303' OR
hucs.huc12rng = '020700090601' OR
hucs.huc12rng = '020700090602' OR
hucs.huc12rng = '030101030102' OR
hucs.huc12rng = '030101070202' OR
hucs.huc12rng = '030102050709' OR
hucs.huc12rng = '030802030307' OR
hucs.huc12rng = '030902060900' OR
hucs.huc12rng = '031300110502' OR
hucs.huc12rng = '031300110706' OR
hucs.huc12rng = '031401010502' OR
hucs.huc12rng = '031401020103' OR
hucs.huc12rng = '031401020302' OR
hucs.huc12rng = '031401030806' OR
hucs.huc12rng = '031401050403' OR
hucs.huc12rng = '031402030604' OR
hucs.huc12rng = '031403050602' OR
hucs.huc12rng = '031501040101' OR
hucs.huc12rng = '031501040904' OR
hucs.huc12rng = '031501041004' OR
hucs.huc12rng = '031501070401' OR
hucs.huc12rng = '031602040101' OR
hucs.huc12rng = '040301050501' OR
hucs.huc12rng = '040301050602' OR
hucs.huc12rng = '040302020303' OR
hucs.huc12rng = '040500012607' OR
hucs.huc12rng = '040601030501' OR
hucs.huc12rng = '040801040203' OR
hucs.huc12rng = '041401020403' OR
hucs.huc12rng = '041501010104' OR
hucs.huc12rng = '050800030407' OR
hucs.huc12rng = '050800030804' OR
hucs.huc12rng = '051002040505' OR
hucs.huc12rng = '051301080404' OR
hucs.huc12rng = '060300030103' OR
hucs.huc12rng = '060300030203' OR
hucs.huc12rng = '070400080206' OR
hucs.huc12rng = '070500050108' OR
hucs.huc12rng = '070700040406' OR
hucs.huc12rng = '070801010601' OR
hucs.huc12rng = '070801010605' OR
hucs.huc12rng = '070801041805' OR
hucs.huc12rng = '070900040203' OR
hucs.huc12rng = '071300030302' OR
hucs.huc12rng = '071300031003' OR
hucs.huc12rng = '080101000601' OR
hucs.huc12rng = '080302041102' OR
hucs.huc12rng = '080401020406' OR
hucs.huc12rng = '080401030804' OR
hucs.huc12rng = '080402020705' OR
hucs.huc12rng = '080402050403' OR
hucs.huc12rng = '080402070203' OR
hucs.huc12rng = '080602021107' OR
hucs.huc12rng = '080602060304' OR
hucs.huc12rng = '080702020804' OR
hucs.huc12rng = '080702030205' OR
hucs.huc12rng = '080801020511' OR
hucs.huc12rng = '080801030402' OR
hucs.huc12rng = '080802030406' OR
hucs.huc12rng = '080903010505' OR
hucs.huc12rng = '100301012003' OR
hucs.huc12rng = '100301012006' OR
hucs.huc12rng = '100301021502' OR
hucs.huc12rng = '100301031003' OR
hucs.huc12rng = '100301040504' OR
hucs.huc12rng = '100302010203' OR
hucs.huc12rng = '100401030702' OR
hucs.huc12rng = '100402011405' OR
hucs.huc12rng = '100402040302' OR
hucs.huc12rng = '100500010101' OR
hucs.huc12rng = '100500090102' OR
hucs.huc12rng = '100500140201' OR
hucs.huc12rng = '100700020503' OR
hucs.huc12rng = '100700020602' OR
hucs.huc12rng = '100700021402' OR
hucs.huc12rng = '100700030201' OR
hucs.huc12rng = '100700030502' OR
hucs.huc12rng = '100800010103' OR
hucs.huc12rng = '100800010603' OR
hucs.huc12rng = '100800010604' OR
hucs.huc12rng = '100800030105' OR
hucs.huc12rng = '100800080403' OR
hucs.huc12rng = '100800080502' OR
hucs.huc12rng = '100800100107' OR
hucs.huc12rng = '100800100203' OR
hucs.huc12rng = '100800100401' OR
hucs.huc12rng = '100800130201' OR
hucs.huc12rng = '100800130204' OR
hucs.huc12rng = '100800130206' OR
hucs.huc12rng = '100901010207' OR
hucs.huc12rng = '100902010208' OR
hucs.huc12rng = '100902060106' OR
hucs.huc12rng = '101102010102' OR
hucs.huc12rng = '101201090402' OR
hucs.huc12rng = '101201090604' OR
hucs.huc12rng = '101201110605' OR
hucs.huc12rng = '101402010804' OR
hucs.huc12rng = '101500031602' OR
hucs.huc12rng = '101600040506' OR
hucs.huc12rng = '101800020303' OR
hucs.huc12rng = '101800020603' OR
hucs.huc12rng = '101800050303' OR
hucs.huc12rng = '101800070301' OR
hucs.huc12rng = '101800110107' OR
hucs.huc12rng = '101800140105' OR
hucs.huc12rng = '101900020602' OR
hucs.huc12rng = '101900020607' OR
hucs.huc12rng = '101900020703' OR
hucs.huc12rng = '101900040303' OR
hucs.huc12rng = '101900070805' OR
hucs.huc12rng = '101900180604' OR
hucs.huc12rng = '110100090201' OR
hucs.huc12rng = '110100130404' OR
hucs.huc12rng = '110200100501' OR
hucs.huc12rng = '110400010401' OR
hucs.huc12rng = '110800010104' OR
hucs.huc12rng = '110800020108' OR
hucs.huc12rng = '110800030108' OR
hucs.huc12rng = '110800040105' OR
hucs.huc12rng = '111102070402' OR
hucs.huc12rng = '111401020108' OR
hucs.huc12rng = '120301050407' OR
hucs.huc12rng = '120302030301' OR
hucs.huc12rng = '120701040106' OR
hucs.huc12rng = '120701040210' OR
hucs.huc12rng = '121001010401' OR
hucs.huc12rng = '121101010406' OR
hucs.huc12rng = '121101100104' OR
hucs.huc12rng = '130100020708' OR
hucs.huc12rng = '130100020906' OR
hucs.huc12rng = '130100030103' OR
hucs.huc12rng = '130100030201' OR
hucs.huc12rng = '130100030402' OR
hucs.huc12rng = '130100030407' OR
hucs.huc12rng = '130100030601' OR
hucs.huc12rng = '130100030606' OR
hucs.huc12rng = '130100040704' OR
hucs.huc12rng = '130100050406' OR
hucs.huc12rng = '130201010206' OR
hucs.huc12rng = '130201010702' OR
hucs.huc12rng = '130201010801' OR
hucs.huc12rng = '130201011103' OR
hucs.huc12rng = '130201020804' OR
hucs.huc12rng = '130201021003' OR
hucs.huc12rng = '130201021204' OR
hucs.huc12rng = '130202010102' OR
hucs.huc12rng = '130202010204' OR
hucs.huc12rng = '130202010610' OR
hucs.huc12rng = '130202030201' OR
hucs.huc12rng = '130202030203' OR
hucs.huc12rng = '130202030401' OR
hucs.huc12rng = '130202030402' OR
hucs.huc12rng = '130202030802' OR
hucs.huc12rng = '130202030903' OR
hucs.huc12rng = '130202040105' OR
hucs.huc12rng = '130202040106' OR
hucs.huc12rng = '130202040403' OR
hucs.huc12rng = '130202050101' OR
hucs.huc12rng = '130202070401' OR
hucs.huc12rng = '130202070405' OR
hucs.huc12rng = '130202080103' OR
hucs.huc12rng = '130202090102' OR
hucs.huc12rng = '130202090103' OR
hucs.huc12rng = '130202090605' OR
hucs.huc12rng = '130202110205' OR
hucs.huc12rng = '130202110504' OR
hucs.huc12rng = '130301020201' OR
hucs.huc12rng = '130302010203' OR
hucs.huc12rng = '130302010806' OR
hucs.huc12rng = '130302010809' OR
hucs.huc12rng = '130302010812' OR
hucs.huc12rng = '130302020204' OR
hucs.huc12rng = '130403030301' OR
hucs.huc12rng = '130500011002' OR
hucs.huc12rng = '130500011101' OR
hucs.huc12rng = '130500011102' OR
hucs.huc12rng = '130500030501' OR
hucs.huc12rng = '130500030503' OR
hucs.huc12rng = '130500031102' OR
hucs.huc12rng = '130500031201' OR
hucs.huc12rng = '130500031202' OR
hucs.huc12rng = '130500031203' OR
hucs.huc12rng = '130500031401' OR
hucs.huc12rng = '130500031501' OR
hucs.huc12rng = '130500031502' OR
hucs.huc12rng = '130500031601' OR
hucs.huc12rng = '130500031704' OR
hucs.huc12rng = '130500031705' OR
hucs.huc12rng = '130500040101' OR
hucs.huc12rng = '130500040401' OR
hucs.huc12rng = '130600050201' OR
hucs.huc12rng = '130600050302' OR
hucs.huc12rng = '130600080101' OR
hucs.huc12rng = '130600080102' OR
hucs.huc12rng = '130600080103' OR
hucs.huc12rng = '130600080201' OR
hucs.huc12rng = '130600090101' OR
hucs.huc12rng = '130600090102' OR
hucs.huc12rng = '130600090103' OR
hucs.huc12rng = '130600100101' OR
hucs.huc12rng = '130600100102' OR
hucs.huc12rng = '130600100103' OR
hucs.huc12rng = '130600100104' OR
hucs.huc12rng = '130600100201' OR
hucs.huc12rng = '130600100202' OR
hucs.huc12rng = '130600100301' OR
hucs.huc12rng = '130600100302' OR
hucs.huc12rng = '130600100303' OR
hucs.huc12rng = '130600100304' OR
hucs.huc12rng = '130600100305' OR
hucs.huc12rng = '130600100401' OR
hucs.huc12rng = '130600100402' OR
hucs.huc12rng = '130600111101' OR
hucs.huc12rng = '140100050204' OR
hucs.huc12rng = '140100050403' OR
hucs.huc12rng = '140100050701' OR
hucs.huc12rng = '140100051306' OR
hucs.huc12rng = '140100051411' OR
hucs.huc12rng = '140200050202' OR
hucs.huc12rng = '140200060301' OR
hucs.huc12rng = '140300020603' OR
hucs.huc12rng = '140300020901' OR
hucs.huc12rng = '140300030701' OR
hucs.huc12rng = '140300050304' OR
hucs.huc12rng = '140401010204' OR
hucs.huc12rng = '140401010809' OR
hucs.huc12rng = '140401011004' OR
hucs.huc12rng = '140401060304' OR
hucs.huc12rng = '140401060309' OR
hucs.huc12rng = '140500010701' OR
hucs.huc12rng = '140500010704' OR
hucs.huc12rng = '140500010705' OR
hucs.huc12rng = '140500030204' OR
hucs.huc12rng = '140500050401' OR
hucs.huc12rng = '140600030204' OR
hucs.huc12rng = '140600030901' OR
hucs.huc12rng = '140600040302' OR
hucs.huc12rng = '140600090206' OR
hucs.huc12rng = '140600090207' OR
hucs.huc12rng = '140801011601' OR
hucs.huc12rng = '140801011602' OR
hucs.huc12rng = '140801050106' OR
hucs.huc12rng = '140801050902' OR
hucs.huc12rng = '140801061304' OR
hucs.huc12rng = '140801061306' OR
hucs.huc12rng = '140801061601' OR
hucs.huc12rng = '140802040403' OR
hucs.huc12rng = '150100010106' OR
hucs.huc12rng = '150100020104' OR
hucs.huc12rng = '150100020106' OR
hucs.huc12rng = '150100020107' OR
hucs.huc12rng = '150100020108' OR
hucs.huc12rng = '150100020909' OR
hucs.huc12rng = '150100040203' OR
hucs.huc12rng = '150100040204' OR
hucs.huc12rng = '150100040804' OR
hucs.huc12rng = '150100040808' OR
hucs.huc12rng = '150100041004' OR
hucs.huc12rng = '150100050301' OR
hucs.huc12rng = '150100060503' OR
hucs.huc12rng = '150100080807' OR
hucs.huc12rng = '150200060101' OR
hucs.huc12rng = '150200090108' OR
hucs.huc12rng = '150200110106' OR
hucs.huc12rng = '150200110107' OR
hucs.huc12rng = '150200160502' OR
hucs.huc12rng = '150200160702' OR
hucs.huc12rng = '150301030304' OR
hucs.huc12rng = '150301030406' OR
hucs.huc12rng = '150302010702' OR
hucs.huc12rng = '150400050503' OR
hucs.huc12rng = '150400050707' OR
hucs.huc12rng = '150400050711' OR
hucs.huc12rng = '150400070103' OR
hucs.huc12rng = '150400070209' OR
hucs.huc12rng = '150400070407' OR
hucs.huc12rng = '150502030509' OR
hucs.huc12rng = '150502030511' OR
hucs.huc12rng = '150503010705' OR
hucs.huc12rng = '150602010608' OR
hucs.huc12rng = '150602020104' OR
hucs.huc12rng = '150701020503' OR
hucs.huc12rng = '150701020506' OR
hucs.huc12rng = '150701030302' OR
hucs.huc12rng = '160101010103' OR
hucs.huc12rng = '160101010202' OR
hucs.huc12rng = '160101020206' OR
hucs.huc12rng = '160102010702' OR
hucs.huc12rng = '160102020403' OR
hucs.huc12rng = '160102020702' OR
hucs.huc12rng = '160300020401' OR
hucs.huc12rng = '160300020403' OR
hucs.huc12rng = '160300040405' OR
hucs.huc12rng = '160300040504' OR
hucs.huc12rng = '160300050101' OR
hucs.huc12rng = '160300050203' OR
hucs.huc12rng = '160300051403' OR
hucs.huc12rng = '160300060105' OR
hucs.huc12rng = '160300060309' OR
hucs.huc12rng = '160300070207' OR
hucs.huc12rng = '160300070501' OR
hucs.huc12rng = '160501020505' OR
hucs.huc12rng = '160502010303' OR
hucs.huc12rng = '170200010608' OR
hucs.huc12rng = '170200060402' OR
hucs.huc12rng = '170200080701' OR
hucs.huc12rng = '170200100309' OR
hucs.huc12rng = '170300010405' OR
hucs.huc12rng = '170402020202' OR
hucs.huc12rng = '170402040403' OR
hucs.huc12rng = '170402150502' OR
hucs.huc12rng = '170402200305' OR
hucs.huc12rng = '170402210403' OR
hucs.huc12rng = '170501140401' OR
hucs.huc12rng = '170701030301' OR
hucs.huc12rng = '170701030606' OR
hucs.huc12rng = '170701050202' OR
hucs.huc12rng = '170703050710' OR
hucs.huc12rng = '170703061103' OR
hucs.huc12rng = '170703061105' OR
hucs.huc12rng = '170900020404' OR
hucs.huc12rng = '170900120302' OR
hucs.huc12rng = '171001030202' OR
hucs.huc12rng = '171001030203' OR
hucs.huc12rng = '171100090602' OR
hucs.huc12rng = '171100100302' OR
hucs.huc12rng = '171100140106' OR
hucs.huc12rng = '171200010105' OR
hucs.huc12rng = '171200060402' OR
hucs.huc12rng = '180101030101' OR
hucs.huc12rng = '180101030205' OR
hucs.huc12rng = '180101100403' OR
hucs.huc12rng = '180201150403' OR
hucs.huc12rng = '180201160204' OR
hucs.huc12rng = '180201510106' OR
hucs.huc12rng = '180300010606' OR
hucs.huc12rng = '180300030503' OR
hucs.huc12rng = '180300040102' OR
hucs.huc12rng = '180300060203' OR
hucs.huc12rng = '180400010501' OR
hucs.huc12rng = '180500060207' OR
hucs.huc12rng = '180600010204' OR
hucs.huc12rng = '180800010205' OR
hucs.huc12rng = '180800010306' OR
hucs.huc12rng = '180800020108' OR
hucs.huc12rng = '180901010404' OR
hucs.huc12rng = '180901010605' OR
hucs.huc12rng = '180901020209' OR
hucs.huc12rng = '180901020803' OR
hucs.huc12rng = '180901030201' OR
hucs.huc12rng = '180901030203' OR
hucs.huc12rng = '180901030205' OR
hucs.huc12rng = '180901030206' OR
hucs.huc12rng = '180901030207' OR
hucs.huc12rng = '180902010305' OR
hucs.huc12rng = '180902010407' OR
hucs.huc12rng = '180902050303' OR
hucs.huc12rng = '180902061001' OR
hucs.huc12rng = '180902061301' OR
hucs.huc12rng = '181002010202' OR
hucs.huc12rng = '181002010203'
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
--select * from #polyMax

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
--select * from #polyData

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
WHERE species_cd = 'aMXSPx'
    GROUP BY #polyData.bndValue, 
             #polyData.huc12rng,
             #polyData.padus1_4,
             #polyData.na_l2code,
             lu_boundary_species.species_cd;    -- 267,849,366 records
--select * from #distSpp

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
--select * from #summSpp

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
select * from qtblRarityXLS

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

