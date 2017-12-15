
CREATE TABLE CMSummary
(ID INT NOT NULL AUTO_INCREMENT, CM_Ref VARCHAR(255) NOT NULL, 
Name VARCHAR(255) NULL, Family VARCHAR(255) NULL, Target VARCHAR(255) NULL, 
Source VARCHAR(255) NULL, PRIMARY KEY(ID), INDEX(CM_Ref))
SELECT CM.name AS "CM_Ref", 
TRIM(SUBSTR(REPLACE(CMhasName.value,'"^^xsd:string',''), 2)) AS 'Name', 
TRIM(SUBSTR(REPLACE(famName.value,'"^^xsd:string',''), 2)) AS 'Family', 
TRIM(SUBSTR(REPLACE(Tname.value,'"^^xsd:string',''), 2)) AS 'Target', 
TRIM(SUBSTR(REPLACE(Sname.value,'"^^xsd:string',''), 2)) AS 'Source' 
FROM Individual CM
JOIN DataPropertyInstance CMhasName ON CM.class='VettedMetaphor' AND CMhasName.property='hasName' AND CMhasName.domainIndividual=CM.name 
LEFT JOIN ObjectPropertyInstance hasFam ON CM.name=hasFam.domainIndividual  AND hasFam.property='isInMetaphorFamily' 
LEFT JOIN Individual fam ON fam.name=hasFam.rangeIndividual 
LEFT JOIN DataPropertyInstance famName ON famName.property='hasName' AND famName.domainIndividual=fam.name
JOIN ObjectPropertyInstance hasTarget ON hasTarget.property='hasTargetSchema' AND hasTarget.domainIndividual = CM.name 
JOIN Individual T ON hasTarget.rangeIndividual=T.name 
JOIN ObjectPropertyInstance hasSource ON hasSource.property="hasSourceSchema" AND hasSource.domainIndividual = CM.name 
JOIN Individual S ON hasSource.rangeIndividual=S.name 
JOIN DataPropertyInstance Tname ON Tname.property='hasName' AND Tname.domainIndividual=T.name 
JOIN DataPropertyInstance Sname ON Sname.property='hasName' AND Sname.domainIndividual=S.name; 

CREATE TABLE LMSummary (ID INT NOT NULL AUTO_INCREMENT, LM_Ref VARCHAR(255) NULL, Target VARCHAR(255) NULL, Source VARCHAR(255) NULL, Text TEXT NULL, CM_Ref VARCHAR(255) NULL, PRIMARY KEY(ID), INDEX(CM_Ref)) SELECT LM.name AS "LM_Ref", TRIM(SUBSTR(REPLACE(T.value,'"^^xsd:string',''),2)) AS "Target", TRIM(SUBSTR(REPLACE(S.value,'"^^xsd:string',''),2)) AS "Source", TRIM(SUBSTR(REPLACE(hasText.value,'"^^xsd:string',''),2)) AS 'Text', hasInst.rangeIndividual AS 'CM_Ref' FROM Individual Ex LEFT JOIN ObjectPropertyInstance hasEx ON Ex.name=hasEx.rangeIndividual AND Ex.class='Example' JOIN DataPropertyInstance hasText ON hasText.property="hasSentence" AND hasText.domainIndividual=Ex.name JOIN Individual LM ON hasEx.domainIndividual=LM.name JOIN DataPropertyInstance T ON T.property='hasLinguisticTarget' AND T.domainIndividual=LM.name JOIN DataPropertyInstance S ON S.property='hasLinguisticSource' AND S.domainIndividual=LM.name LEFT JOIN ObjectPropertyInstance hasInst ON hasInst.property='isInstanceOfMetaphor' AND hasInst.domainIndividual=LM.name;

INSERT INTO LMSummary (LM_Ref, Target, Source, Text, CM_Ref) SELECT NULL, NULL, NULL, TRIM(SUBSTR(REPLACE(hasText.value,'"^^xsd:string',''),2)) AS 'Text', CM.name AS "CM_Ref" FROM Individual Ex LEFT JOIN ObjectPropertyInstance hasEx ON Ex.name=hasEx.rangeIndividual AND Ex.class='Example' JOIN DataPropertyInstance hasText ON hasText.property="hasSentence" AND hasText.domainIndividual=Ex.name JOIN Individual CM ON hasEx.domainIndividual=CM.name AND CM.class='VettedMetaphor';
