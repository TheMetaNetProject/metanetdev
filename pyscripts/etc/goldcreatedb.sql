DROP TABLE IF EXISTS `sent`;
CREATE TABLE `sent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sid` VARCHAR(128) NOT NULL,
  `text` MEDIUMTEXT NOT NULL,
  `mtext` MEDIUMTEXT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_unique` (`id`),
  UNIQUE KEY `sid_unique` (`sid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `target`;
CREATE TABLE `target` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `concept` VARCHAR(45) NOT NULL,
  `schemaname` VARCHAR(128) NOT NULL,
  `lemma` VARCHAR(128) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_unique` (`id`),
  UNIQUE KEY `lemma_unique` (`lemma`),
  INDEX `concept_idx` (`concept` ASC),
  INDEX `sname_idx` (`schemaname` ASC),
  INDEX `lemma_idx` (`lemma` ASC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `ts_join`;
CREATE TABLE `ts_join` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sent_id` int(11) NOT NULL,
  `target_id` int(11) NOT NULL,
  `wordform` VARCHAR(128),
  `wfstart` SMALLINT,
  `wfend` SMALLINT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_unique` (`id`),
  INDEX `sent_idx` (`sent_id` ASC),
  INDEX `target_idx` (`target_id` ASC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `lemma`;
CREATE TABLE `lemma` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lemma` VARCHAR(128) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_unique` (`id`),
  UNIQUE KEY `lemma_unique` (`lemma`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `ls_join`;
CREATE TABLE `ls_join` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sent_id` int(11) NOT NULL,
  `lemma_id` int(11) NOT NULL,
  `wordform` VARCHAR(128),
  `wfstart` SMALLINT,
  `wfend` SMALLINT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_unique` (`id`),
  INDEX `sent_idx` (`sent_id` ASC),
  INDEX `lemma_idx` (`lemma_id` ASC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
