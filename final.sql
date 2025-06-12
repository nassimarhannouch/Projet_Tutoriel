-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: final
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `appcours_cours`
--

DROP TABLE IF EXISTS `appcours_cours`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appcours_cours` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `filiere_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `appcours_cours_filiere_id_0680d7d0_fk_appcours_filiere_id` (`filiere_id`),
  CONSTRAINT `appcours_cours_filiere_id_0680d7d0_fk_appcours_filiere_id` FOREIGN KEY (`filiere_id`) REFERENCES `appcours_filiere` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appcours_cours`
--

LOCK TABLES `appcours_cours` WRITE;
/*!40000 ALTER TABLE `appcours_cours` DISABLE KEYS */;
INSERT INTO `appcours_cours` VALUES (1,'JEE',1),(2,'ML',2),(3,'RO',1),(4,'UNIX',2),(5,'UML',2),(6,'JAVA',1),(7,'PROBA',1);
/*!40000 ALTER TABLE `appcours_cours` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appcours_courseresource`
--

DROP TABLE IF EXISTS `appcours_courseresource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appcours_courseresource` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `course_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `resource_link` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appcours_courseresource`
--

LOCK TABLES `appcours_courseresource` WRITE;
/*!40000 ALTER TABLE `appcours_courseresource` DISABLE KEYS */;
INSERT INTO `appcours_courseresource` VALUES (1,'JAVA','http://example.com/resources/math101.pdf','Support de cours Mathématiques 1ère année'),(2,'RO','http://example.com/resources/python_intro.pdf','Introduction à Python'),(3,'ML','http://example.com/resources/physique_mecanique.pdf','Cours de mécanique classique'),(4,'PROBA','https://www.bing.com/search?pglt=2339&q=probabilite&cvid=56c3b33dc5ce498293caccc3a07df46b&gs_lcrp=EgRlZGdlKgYIABBFGDkyBggAEEUYOdIBCDI2NTRqMGoxqAIIsAIB&FORM=ANNTA1&PC=U531','probabilites en ligne');
/*!40000 ALTER TABLE `appcours_courseresource` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appcours_feedback`
--

DROP TABLE IF EXISTS `appcours_feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appcours_feedback` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `note` int NOT NULL,
  `commentaire` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_creation` datetime(6) NOT NULL,
  `sentiment` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cours_id` bigint NOT NULL,
  `anonyme` tinyint(1) NOT NULL,
  `date_cours` date DEFAULT NULL,
  `etudiant_id` bigint DEFAULT NULL,
  `partager` tinyint(1) NOT NULL,
  `professeur_id` bigint DEFAULT NULL,
  `suggestions` longtext COLLATE utf8mb4_unicode_ci,
  `recommendations` longtext COLLATE utf8mb4_unicode_ci,
  `theme_pred` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `appcours_feedback_cours_id_98fd33c6_fk_appcours_cours_id` (`cours_id`),
  KEY `appcours_feedback_etudiant_id_6f3344ef_fk_appcours_` (`etudiant_id`),
  KEY `appcours_feedback_professeur_id_6e5d0a12_fk_appcours_` (`professeur_id`),
  CONSTRAINT `appcours_feedback_cours_id_98fd33c6_fk_appcours_cours_id` FOREIGN KEY (`cours_id`) REFERENCES `appcours_cours` (`id`),
  CONSTRAINT `appcours_feedback_etudiant_id_6f3344ef_fk_appcours_` FOREIGN KEY (`etudiant_id`) REFERENCES `appcours_utilisateur` (`id`),
  CONSTRAINT `appcours_feedback_professeur_id_6e5d0a12_fk_appcours_` FOREIGN KEY (`professeur_id`) REFERENCES `appcours_professeur` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appcours_feedback`
--

LOCK TABLES `appcours_feedback` WRITE;
/*!40000 ALTER TABLE `appcours_feedback` DISABLE KEYS */;
INSERT INTO `appcours_feedback` VALUES (6,4,'good','2025-05-08 18:18:16.600176','positif',2,0,NULL,NULL,0,NULL,NULL,NULL,NULL),(7,4,'Le cours manque de clarté et les explications sont souvent confuses.','2025-05-08 18:19:09.879548','négatif',1,0,NULL,NULL,0,NULL,NULL,NULL,NULL),(10,4,'Le cours était très clair et bien structuré, j’ai enfin compris cette notion difficile grâce à vous.','2025-05-10 13:01:31.431123','positif',3,0,NULL,NULL,0,NULL,NULL,NULL,NULL),(14,3,'good','2025-05-17 18:20:09.825644','positif',4,0,NULL,NULL,0,NULL,NULL,NULL,NULL),(17,4,'Exellent','2025-05-17 18:43:47.474222','positif',5,0,NULL,NULL,0,NULL,NULL,NULL,NULL),(24,5,'verry good','2025-05-18 15:31:43.536857','positif',1,0,'2025-05-02',9,1,1,'good',NULL,NULL),(27,3,'exellent','2025-06-07 00:32:24.610250','positif',1,0,'2025-06-27',9,1,1,'exellent',NULL,NULL),(28,2,'moyen','2025-06-07 12:32:37.703143','neutre',3,0,'2025-06-05',9,1,2,'amelioration',NULL,NULL),(34,1,'I didn\'t understand anything, it was confusing.','2025-06-07 12:43:31.120545','négatif',1,0,'2025-06-04',9,1,1,'amm',NULL,NULL),(38,3,'good','2025-06-07 14:01:27.109080','positif',1,0,'2025-06-12',9,1,1,'good',NULL,NULL),(39,1,'There is too much theoretical content without any practical examples.','2025-06-07 14:02:47.228981','négatif',2,0,'2025-06-06',9,1,3,'hjhjhj',NULL,NULL),(44,1,'Le cours est ennuyeux et mal expliqué.','2025-06-07 14:33:41.614446','négatif',1,0,'2025-06-05',9,1,1,'gfff',NULL,NULL),(45,1,'exellent','2025-06-07 15:07:29.371455','positif',2,0,'2025-06-18',9,1,3,'fg',NULL,NULL),(46,1,'Le cours est vraiment ennuyeux et manque de clarté.','2025-06-07 15:08:15.466027','négatif',2,0,'2025-06-04',9,1,3,'jhjhk',NULL,NULL),(47,1,'Les supports de cours sont mal organisés et difficiles à comprendre.','2025-06-08 00:24:25.481484','négatif',2,0,'2025-06-12',9,1,3,'hjkjk',NULL,NULL),(50,1,'\'The instructor didn’t explain the concepts clearly.\'','2025-06-08 13:14:24.917336','négatif',1,0,'2025-06-18',9,1,1,'hkjk',NULL,NULL),(51,1,'Lack of examples made it hard to understand concepts.','2025-06-09 15:16:43.463977','négatif',2,0,'2025-06-04',9,1,3,'ameliorer',NULL,NULL),(52,1,'The professor was not responsive to questions.','2025-06-10 23:46:37.291865','négatif',1,1,'2025-06-03',NULL,0,1,'ameliorer','Encourager l\'enseignant à être plus accessible.; Améliorer la qualité des explications.; Former l\'enseignant aux méthodes pédagogiques modernes.','teacher'),(53,1,'The professor was not responsive to questions.','2025-06-10 23:48:53.634727','négatif',1,1,'2025-06-03',NULL,0,1,'ameliorer','Encourager l\'enseignant à être plus accessible.; Améliorer la qualité des explications.; Former l\'enseignant aux méthodes pédagogiques modernes.','teacher'),(54,1,'The professor was not responsive to questions.','2025-06-11 11:21:51.768282','négatif',1,1,'2025-06-12',NULL,0,1,'','Encourager l\'enseignant à être plus accessible.; Améliorer la qualité des explications.; Former l\'enseignant aux méthodes pédagogiques modernes.','teacher'),(55,1,'\'The professor was not responsive to questions.\'','2025-06-11 11:38:24.219835','négatif',1,0,'2025-06-04',9,1,1,'','Encourager l\'enseignant à être plus accessible.; Améliorer la qualité des explications.; Former l\'enseignant aux méthodes pédagogiques modernes.','teacher'),(56,1,'\'\'\'The professor was not responsive to questions.\'\'\'','2025-06-11 23:29:59.599548','négatif',1,0,'2025-06-03',9,1,1,'','Encourager l\'enseignant à être plus accessible.; Améliorer la qualité des explications.; Former l\'enseignant aux méthodes pédagogiques modernes.','teacher'),(57,1,'The instructor didn\'t explain the concepts clearly.','2025-06-12 13:09:38.121555','négatif',1,0,'2025-06-04',9,1,1,'More exercises.','Analyser le feedback pour des améliorations générales.; Organiser une réunion avec les étudiants concernés.','general'),(58,1,'le cours manque de clarté dans les explications.','2025-06-12 13:14:33.558612','négatif',6,1,'2025-06-11',NULL,0,6,'améliorer les explications on utilisant des exemples.','Mettre à jour le contenu du cours.; Fournir plus de matériel d\'apprentissage.; Adapter le contenu au niveau des étudiants.','course content'),(59,1,'The instructor didn\'t explain the concepts clearly.','2025-06-12 14:15:33.370889','négatif',1,0,'2025-06-03',9,1,1,'More exercises.','Analyser le feedback pour des améliorations générales.; Organiser une réunion avec les étudiants concernés.','general');
/*!40000 ALTER TABLE `appcours_feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appcours_filiere`
--

DROP TABLE IF EXISTS `appcours_filiere`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appcours_filiere` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appcours_filiere`
--

LOCK TABLES `appcours_filiere` WRITE;
/*!40000 ALTER TABLE `appcours_filiere` DISABLE KEYS */;
INSERT INTO `appcours_filiere` VALUES (1,'IID','informatique et ingenierie des donnee'),(2,'GI','geni info');
/*!40000 ALTER TABLE `appcours_filiere` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appcours_modeevaluation`
--

DROP TABLE IF EXISTS `appcours_modeevaluation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appcours_modeevaluation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `mode` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pourcentage` int NOT NULL,
  `cours_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `appcours_modeevaluation_cours_id_2c6ebab9_fk_appcours_cours_id` (`cours_id`),
  CONSTRAINT `appcours_modeevaluation_cours_id_2c6ebab9_fk_appcours_cours_id` FOREIGN KEY (`cours_id`) REFERENCES `appcours_cours` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appcours_modeevaluation`
--

LOCK TABLES `appcours_modeevaluation` WRITE;
/*!40000 ALTER TABLE `appcours_modeevaluation` DISABLE KEYS */;
INSERT INTO `appcours_modeevaluation` VALUES (1,'TP',10,1),(2,'projet',20,1),(3,'examen',70,1),(4,'TP',10,5),(5,'projet',20,5),(6,'examen',70,5);
/*!40000 ALTER TABLE `appcours_modeevaluation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appcours_notes`
--

DROP TABLE IF EXISTS `appcours_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appcours_notes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `note` decimal(4,2) NOT NULL,
  `date_creation` datetime(6) NOT NULL,
  `cours_id` bigint NOT NULL,
  `etudiant_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `appcours_notes_etudiant_id_cours_id_77692504_uniq` (`etudiant_id`,`cours_id`),
  KEY `appcours_notes_cours_id_4c9a4ab0_fk_appcours_cours_id` (`cours_id`),
  CONSTRAINT `appcours_notes_cours_id_4c9a4ab0_fk_appcours_cours_id` FOREIGN KEY (`cours_id`) REFERENCES `appcours_cours` (`id`),
  CONSTRAINT `appcours_notes_etudiant_id_37b3afc8_fk_appcours_utilisateur_id` FOREIGN KEY (`etudiant_id`) REFERENCES `appcours_utilisateur` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appcours_notes`
--

LOCK TABLES `appcours_notes` WRITE;
/*!40000 ALTER TABLE `appcours_notes` DISABLE KEYS */;
INSERT INTO `appcours_notes` VALUES (5,18.00,'2025-05-19 12:55:25.000000',1,2),(6,15.75,'2025-05-19 12:55:25.000000',2,2),(7,15.65,'2025-05-19 13:29:25.000000',1,9),(8,14.50,'2025-05-19 13:33:26.000000',4,9),(9,16.25,'2025-05-19 13:33:26.000000',2,9),(10,11.75,'2025-05-19 13:33:26.000000',3,9),(11,20.00,'2025-06-08 17:26:26.000000',6,9),(12,18.00,'2025-06-08 17:26:26.000000',6,2);
/*!40000 ALTER TABLE `appcours_notes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appcours_professeur`
--

DROP TABLE IF EXISTS `appcours_professeur`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appcours_professeur` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telephone` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appcours_professeur`
--

LOCK TABLES `appcours_professeur` WRITE;
/*!40000 ALTER TABLE `appcours_professeur` DISABLE KEYS */;
INSERT INTO `appcours_professeur` VALUES (1,'Rhannouch','Nassima','nassimarhannouch123@gmail.com','0656535443'),(2,'Hadil','Rahoui','hadil123@gmail.com','7685756'),(3,'Khassoumi','Hanane','hanane123@gmail.com','74645353'),(5,'Rhannouch','Yasmine','yassmine@gmail.com','989737'),(6,'Rhannouch','Tasnime','tasnime@gmail.com','6889807'),(7,'Rahui','najlae','najlae@gmail.com','5767686');
/*!40000 ALTER TABLE `appcours_professeur` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appcours_professeur_cours`
--

DROP TABLE IF EXISTS `appcours_professeur_cours`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appcours_professeur_cours` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `professeur_id` bigint NOT NULL,
  `cours_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `appcours_professeur_cours_professeur_id_cours_id_5322771d_uniq` (`professeur_id`,`cours_id`),
  KEY `appcours_professeur_cours_cours_id_f2d30606_fk_appcours_cours_id` (`cours_id`),
  CONSTRAINT `appcours_professeur__professeur_id_4c12b857_fk_appcours_` FOREIGN KEY (`professeur_id`) REFERENCES `appcours_professeur` (`id`),
  CONSTRAINT `appcours_professeur_cours_cours_id_f2d30606_fk_appcours_cours_id` FOREIGN KEY (`cours_id`) REFERENCES `appcours_cours` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appcours_professeur_cours`
--

LOCK TABLES `appcours_professeur_cours` WRITE;
/*!40000 ALTER TABLE `appcours_professeur_cours` DISABLE KEYS */;
INSERT INTO `appcours_professeur_cours` VALUES (1,1,1),(3,2,3),(2,3,2),(4,5,5),(5,6,6),(6,7,7);
/*!40000 ALTER TABLE `appcours_professeur_cours` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appcours_promotion`
--

DROP TABLE IF EXISTS `appcours_promotion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appcours_promotion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `annee_debut` int DEFAULT NULL,
  `annee_fin` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appcours_promotion`
--

LOCK TABLES `appcours_promotion` WRITE;
/*!40000 ALTER TABLE `appcours_promotion` DISABLE KEYS */;
INSERT INTO `appcours_promotion` VALUES (1,'2020',NULL,NULL),(2,'Promotion 2023-2026',2023,2026),(3,'Promotion 2024-2027',2024,2027);
/*!40000 ALTER TABLE `appcours_promotion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appcours_utilisateur`
--

DROP TABLE IF EXISTS `appcours_utilisateur`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appcours_utilisateur` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telephone` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `filiere_id` bigint DEFAULT NULL,
  `promotion_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `appcours_utilisateur_filiere_id_6321d55f_fk_appcours_filiere_id` (`filiere_id`),
  KEY `appcours_utilisateur_promotion_id_9384754b_fk_appcours_` (`promotion_id`),
  CONSTRAINT `appcours_utilisateur_filiere_id_6321d55f_fk_appcours_filiere_id` FOREIGN KEY (`filiere_id`) REFERENCES `appcours_filiere` (`id`),
  CONSTRAINT `appcours_utilisateur_promotion_id_9384754b_fk_appcours_` FOREIGN KEY (`promotion_id`) REFERENCES `appcours_promotion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appcours_utilisateur`
--

LOCK TABLES `appcours_utilisateur` WRITE;
/*!40000 ALTER TABLE `appcours_utilisateur` DISABLE KEYS */;
INSERT INTO `appcours_utilisateur` VALUES (2,'pbkdf2_sha256$1000000$4MrDDIrblIEmJSXm5KgVaT$4iaafYUusmJ6J5f1oJZK5z8N/IU2qIxXO68X6AS1tGE=','2025-06-10 23:45:45.484871',0,'etudiant1','','',0,1,'2025-05-03 00:32:55.553988','etudiant1@example.com','0600000000','etudiant',1,2),(3,'pbkdf2_sha256$1000000$bm3VH86ISGfsXzDAoToW4s$hOPuEbxfDJa2LqrjBAp5AGhHvRFniea2M/lQjzZ2uiw=','2025-06-11 00:33:49.216084',0,'chef1','','',0,1,'2025-05-03 00:32:56.015357','chef1@example.com','0611111111','etudiant',1,NULL),(4,'pbkdf2_sha256$1000000$U9J7A0uryvuohm5uPkRN4y$E0ajQ5a8XlAW1WBVXdXtCSSAZAzQa+H0YmJ9AIzipd8=','2025-06-12 17:40:28.239462',1,'admin1','','',1,1,'2025-05-03 00:32:56.487210','admin@example.com','0622222222','administrateur',NULL,NULL),(5,'pbkdf2_sha256$1000000$mG1c17amZ1JcKIKPw7Dod9$yIeofLiG9D0hpaGTwu+aEv09U2+RW8wCo8zzfT+OsSY=','2025-05-03 00:52:56.948407',0,'Wijdane','','',0,1,'2025-05-03 00:52:31.707263','wijdanetaftaf@gmail.com','065434355','etudiant',1,3),(6,'pbkdf2_sha256$1000000$gtFMlDer3zAaCyRqYKQZZP$kycJICoeGiC5UcrG7bVCWdE7oWMqgx7PX52wIubYU7U=','2025-05-03 17:14:48.037927',0,'tasnime','','',0,1,'2025-05-03 17:14:33.503958','tasnime123@gmail.com','06787786','etudiant',2,3),(7,'pbkdf2_sha256$1000000$OKW5S4dSZMDgDIXIyG3ZEt$xYBEdh1PhnhPg+5eKahLQDMf/ACAIfUe7kthCJ1pWTE=',NULL,0,'Jad','0788989786','',0,1,'2025-05-03 17:32:00.928326','hananekhass@gmail.com',NULL,'etudiant',NULL,NULL),(9,'pbkdf2_sha256$1000000$qEE45EieWF6546jyOUfFZE$9iA2npxmMonwtyF+0oihpx2lEMSR6Fe+tT0XCUthNEQ=','2025-06-12 17:29:36.533675',0,'Nassima','0656535443','',0,1,'2025-05-03 17:46:41.044052','nassimarhannouch123@gmail.com','0656535443','etudiant',1,1),(10,'pbkdf2_sha256$1000000$pOqMB3vcTJ3RXjICTrROKE$8lD+JdzBHPLIQFL+zYCN9RYhiokrHEnk10Q8xvQHGZU=',NULL,0,'Khadija','0643526254','',0,1,'2025-05-03 22:10:05.234638','khadija@gmail.com',NULL,'etudiant',NULL,NULL),(12,'pbkdf2_sha256$1000000$FJ9x3c64s5vnZS8wGNkUbP$5PmwhghGssRMkwVY537bUUWuvpfYLwnp08DfOkVD7p4=','2025-05-18 16:40:42.036704',1,'admin','','',1,1,'2025-05-18 16:40:10.955903','nassimarhannouch123@gmail.cm',NULL,'etudiant',1,1),(13,'pbkdf2_sha256$1000000$80ex4IVgIdGLXpf9WHGrMC$wAoCOoS7/3ppEBzi1wn1/tA2ukw9dXtUlMDnojr/aa8=','2025-06-11 00:31:16.334008',0,'chef2025','','',1,1,'2025-05-18 16:45:55.133371','chef@example.com',NULL,'etudiant',2,NULL),(16,'pbkdf2_sha256$1000000$86EgDhwUnYZqqYKEaXo1tt$XQuDcX/X72Ny6bF1hcq9LjDG6nZPxLm8sXDTUrDhHL0=','2025-06-12 17:36:31.078608',0,'hanane','hanane','khassoumi',0,1,'2025-06-09 16:09:55.658278','hanane123@gmail.com',NULL,'chef_filiere',2,2),(17,'pbkdf2_sha256$1000000$Xj7Pc0GWBbkWCnEhK8gyO1$KbYYGCeqKJgDMxVpwp4RjNZfXRhEKaa7R5CVTSrmYvg=','2025-06-11 00:46:50.438558',0,'yasmine','Yasmine','Rhannouch',0,1,'2025-06-10 22:12:40.033438','yassmine123@gmail.com',NULL,'etudiant',1,NULL),(18,'pbkdf2_sha256$1000000$MKzAIwVI8stNNUVCqObDRo$TRmGggPz/D2Bcidns3Pl/HZQNtfwhngbpbOYpNb6a58=',NULL,0,'toria','Toria','Taftaf',0,1,'2025-06-11 12:57:32.626392','toriataftaf@gmail.com',NULL,'etudiant',1,NULL),(20,'pbkdf2_sha256$1000000$0z5CjILfjHl0lQlaMKpme6$y9Hh5SRb/YgXbflHxpVSDLzhUdYKOwYBLe/MmzH3W7M=','2025-06-12 14:40:55.927702',1,'hp','','',1,1,'2025-06-11 21:54:31.546253','hp123@gmail.com',NULL,'etudiant',NULL,NULL),(21,'pbkdf2_sha256$1000000$SRVm8Ma8rYhvIWnyFNtfD7$kCSpMzLWQ4+ASonaFFDa0/BQXaaqWEaiSipAdO8+KIo=',NULL,0,'fozia','','',0,0,'2025-06-12 13:05:03.440393','fozia123@gmail.com','06534576','etudiant',NULL,NULL),(22,'pbkdf2_sha256$1000000$NF4gdhfPNJXDxlCrsNdMN4$BQAb2X/a/WjgMMz3aXTcVvqvpW/gaMPJW2h9yXFDTQE=',NULL,0,'assia','assia','bakhou',0,1,'2025-06-12 14:22:21.006839','assia123@gmail.com',NULL,'chef_filiere',1,NULL);
/*!40000 ALTER TABLE `appcours_utilisateur` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appcours_utilisateur_groups`
--

DROP TABLE IF EXISTS `appcours_utilisateur_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appcours_utilisateur_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `utilisateur_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `appcours_utilisateur_gro_utilisateur_id_group_id_7799ea72_uniq` (`utilisateur_id`,`group_id`),
  KEY `appcours_utilisateur_groups_group_id_6d5a0e31_fk_auth_group_id` (`group_id`),
  CONSTRAINT `appcours_utilisateur_groups_group_id_6d5a0e31_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `appcours_utilisateur_utilisateur_id_e299030d_fk_appcours_` FOREIGN KEY (`utilisateur_id`) REFERENCES `appcours_utilisateur` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appcours_utilisateur_groups`
--

LOCK TABLES `appcours_utilisateur_groups` WRITE;
/*!40000 ALTER TABLE `appcours_utilisateur_groups` DISABLE KEYS */;
INSERT INTO `appcours_utilisateur_groups` VALUES (2,9,1),(1,16,1);
/*!40000 ALTER TABLE `appcours_utilisateur_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appcours_utilisateur_user_permissions`
--

DROP TABLE IF EXISTS `appcours_utilisateur_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appcours_utilisateur_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `utilisateur_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `appcours_utilisateur_use_utilisateur_id_permissio_95fb0b66_uniq` (`utilisateur_id`,`permission_id`),
  KEY `appcours_utilisateur_permission_id_550201a4_fk_auth_perm` (`permission_id`),
  CONSTRAINT `appcours_utilisateur_permission_id_550201a4_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `appcours_utilisateur_utilisateur_id_bc9e62d2_fk_appcours_` FOREIGN KEY (`utilisateur_id`) REFERENCES `appcours_utilisateur` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appcours_utilisateur_user_permissions`
--

LOCK TABLES `appcours_utilisateur_user_permissions` WRITE;
/*!40000 ALTER TABLE `appcours_utilisateur_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `appcours_utilisateur_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (1,'Chef de Filière');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add user',6,'add_utilisateur'),(22,'Can change user',6,'change_utilisateur'),(23,'Can delete user',6,'delete_utilisateur'),(24,'Can view user',6,'view_utilisateur'),(25,'Can add filiere',7,'add_filiere'),(26,'Can change filiere',7,'change_filiere'),(27,'Can delete filiere',7,'delete_filiere'),(28,'Can view filiere',7,'view_filiere'),(29,'Can add promotion',8,'add_promotion'),(30,'Can change promotion',8,'change_promotion'),(31,'Can delete promotion',8,'delete_promotion'),(32,'Can view promotion',8,'view_promotion'),(33,'Can add cours',9,'add_cours'),(34,'Can change cours',9,'change_cours'),(35,'Can delete cours',9,'delete_cours'),(36,'Can view cours',9,'view_cours'),(37,'Can add feedback',10,'add_feedback'),(38,'Can change feedback',10,'change_feedback'),(39,'Can delete feedback',10,'delete_feedback'),(40,'Can view feedback',10,'view_feedback'),(41,'Can add professeur',11,'add_professeur'),(42,'Can change professeur',11,'change_professeur'),(43,'Can delete professeur',11,'delete_professeur'),(44,'Can view professeur',11,'view_professeur'),(45,'Can add dash app',12,'add_dashapp'),(46,'Can change dash app',12,'change_dashapp'),(47,'Can delete dash app',12,'delete_dashapp'),(48,'Can view dash app',12,'view_dashapp'),(49,'Can add stateless app',13,'add_statelessapp'),(50,'Can change stateless app',13,'change_statelessapp'),(51,'Can delete stateless app',13,'delete_statelessapp'),(52,'Can view stateless app',13,'view_statelessapp'),(53,'Can add course resource',14,'add_courseresource'),(54,'Can change course resource',14,'change_courseresource'),(55,'Can delete course resource',14,'delete_courseresource'),(56,'Can view course resource',14,'view_courseresource'),(57,'Can add Mode d\'évaluation',15,'add_modeevaluation'),(58,'Can change Mode d\'évaluation',15,'change_modeevaluation'),(59,'Can delete Mode d\'évaluation',15,'delete_modeevaluation'),(60,'Can view Mode d\'évaluation',15,'view_modeevaluation'),(61,'Can add Note',16,'add_notes'),(62,'Can change Note',16,'change_notes'),(63,'Can delete Note',16,'delete_notes'),(64,'Can view Note',16,'view_notes');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_appcours_utilisateur_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_appcours_utilisateur_id` FOREIGN KEY (`user_id`) REFERENCES `appcours_utilisateur` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(9,'appcours','cours'),(14,'appcours','courseresource'),(10,'appcours','feedback'),(7,'appcours','filiere'),(15,'appcours','modeevaluation'),(16,'appcours','notes'),(11,'appcours','professeur'),(8,'appcours','promotion'),(6,'appcours','utilisateur'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(12,'django_plotly_dash','dashapp'),(13,'django_plotly_dash','statelessapp'),(5,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-05-02 23:28:34.584283'),(2,'contenttypes','0002_remove_content_type_name','2025-05-02 23:28:34.749825'),(3,'auth','0001_initial','2025-05-02 23:28:35.134280'),(4,'auth','0002_alter_permission_name_max_length','2025-05-02 23:28:35.218297'),(5,'auth','0003_alter_user_email_max_length','2025-05-02 23:28:35.218297'),(6,'auth','0004_alter_user_username_opts','2025-05-02 23:28:35.232515'),(7,'auth','0005_alter_user_last_login_null','2025-05-02 23:28:35.238712'),(8,'auth','0006_require_contenttypes_0002','2025-05-02 23:28:35.238712'),(9,'auth','0007_alter_validators_add_error_messages','2025-05-02 23:28:35.250895'),(10,'auth','0008_alter_user_username_max_length','2025-05-02 23:28:35.257249'),(11,'auth','0009_alter_user_last_name_max_length','2025-05-02 23:28:35.267840'),(12,'auth','0010_alter_group_name_max_length','2025-05-02 23:28:35.284942'),(13,'auth','0011_update_proxy_permissions','2025-05-02 23:28:35.289945'),(14,'auth','0012_alter_user_first_name_max_length','2025-05-02 23:28:35.301241'),(15,'appcours','0001_initial','2025-05-02 23:28:35.843662'),(16,'admin','0001_initial','2025-05-02 23:28:36.027592'),(17,'admin','0002_logentry_remove_auto_add','2025-05-02 23:28:36.035716'),(18,'admin','0003_logentry_add_action_flag_choices','2025-05-02 23:28:36.045834'),(19,'sessions','0001_initial','2025-05-02 23:28:36.098834'),(20,'appcours','0002_cours_filiere_promotion_feedback_cours_filiere_and_more','2025-05-05 12:41:46.807477'),(21,'appcours','0003_professeur','2025-05-08 17:58:55.613727'),(22,'appcours','0004_alter_cours_options_alter_feedback_options_and_more','2025-05-18 09:51:36.720582'),(23,'appcours','0005_remove_feedback_contact','2025-05-18 10:03:10.549602'),(24,'appcours','0006_feedback_contact','2025-05-18 10:06:51.839591'),(25,'appcours','0007_remove_feedback_contact','2025-05-18 10:10:20.131502'),(26,'appcours','0008_remove_cours_credit_remove_cours_description_and_more','2025-05-18 13:58:19.915216'),(27,'django_plotly_dash','0001_initial','2025-05-18 21:27:46.786844'),(28,'django_plotly_dash','0002_add_examples','2025-05-18 21:27:46.789802'),(29,'appcours','0009_courseresource_modeevaluation_notes','2025-05-19 10:32:00.053455'),(30,'appcours','0010_feedback_recommendations_feedback_theme_pred','2025-06-10 23:28:57.659478');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_plotly_dash_dashapp`
--

DROP TABLE IF EXISTS `django_plotly_dash_dashapp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_plotly_dash_dashapp` (
  `id` int NOT NULL AUTO_INCREMENT,
  `instance_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(110) COLLATE utf8mb4_unicode_ci NOT NULL,
  `base_state` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `creation` datetime(6) NOT NULL,
  `update` datetime(6) NOT NULL,
  `save_on_change` tinyint(1) NOT NULL,
  `stateless_app_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `instance_name` (`instance_name`),
  UNIQUE KEY `slug` (`slug`),
  KEY `django_plotly_dash_d_stateless_app_id_220444de_fk_django_pl` (`stateless_app_id`),
  CONSTRAINT `django_plotly_dash_d_stateless_app_id_220444de_fk_django_pl` FOREIGN KEY (`stateless_app_id`) REFERENCES `django_plotly_dash_statelessapp` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_plotly_dash_dashapp`
--

LOCK TABLES `django_plotly_dash_dashapp` WRITE;
/*!40000 ALTER TABLE `django_plotly_dash_dashapp` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_plotly_dash_dashapp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_plotly_dash_statelessapp`
--

DROP TABLE IF EXISTS `django_plotly_dash_statelessapp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_plotly_dash_statelessapp` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(110) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_name` (`app_name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_plotly_dash_statelessapp`
--

LOCK TABLES `django_plotly_dash_statelessapp` WRITE;
/*!40000 ALTER TABLE `django_plotly_dash_statelessapp` DISABLE KEYS */;
INSERT INTO `django_plotly_dash_statelessapp` VALUES (1,'StudentDashboard','studentdashboard'),(2,'StudentDashboard_9','studentdashboard_9'),(3,'FeedbackEvaluationApp','feedbackevaluationapp'),(4,'StudentDashboard_13','studentdashboard_13'),(5,'ModesEvaluationParCours','modesevaluationparcours'),(6,'StudentDashboard_2','studentdashboard_2'),(7,'StudentDashboard_16','studentdashboard_16'),(8,'StudentDashboard_20','studentdashboard_20');
/*!40000 ALTER TABLE `django_plotly_dash_statelessapp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('c0l2umg1l71p78aukv6mje12nprccr5p','.eJxVjDsOwjAQBe_iGlmO4y8lPWewdtcbHEC2FCcV4u4QKQW0b2beSyTY1pK2zkuasziLKE6_GwI9uO4g36HemqRW12VGuSvyoF1eW-bn5XD_Dgr08q1BI2jC4JhyCEF5YjuqaD2YOFoXI_rBI48UTA6T9gNEjRMiWkuojBPvD_A8OBc:1uDlVC:jB94L_7aOmVU7CdI15mC6yicZgfON1leq6oe9ZiilHA','2025-05-24 14:48:34.847522'),('gxj9csr70e3vyltogn9ce52njevm02zy','.eJxVjEsOAiEQBe_C2hA-Ao1L93MGAtPdMmogmc_KeHedZBa6fVX1XiLlba1pW2hOE4qL0FacfseSxwe1neA9t1uXY2_rPBW5K_Kgixw60vN6uH8HNS_1W58NjAGiM2yCM1R8VEorB2TZeULNHC2z154DBosOXNYAhBGiV94q8f4A43U3Ew:1uHqSY:klfxMvk2WQTtY-4WIlxq-Zrt6gzICG12aNrxJMar8N4','2025-06-04 20:54:42.481037'),('idwvuler29y0lhi9klhsiglbyb75mhbs','.eJxVjEsOAiEQBe_C2hA-Ao1L93MGAtPdMmogmc_KeHedZBa6fVX1XiLlba1pW2hOE4qL0FacfseSxwe1neA9t1uXY2_rPBW5K_Kgixw60vN6uH8HNS_1W58NjAGiM2yCM1R8VEorB2TZeULNHC2z154DBosOXNYAhBGiV94q8f4A43U3Ew:1uOGyf:QsLo6zboymTZWhn2_SrFJdzUlRksUSPcaDTfJYLshBQ','2025-06-22 14:26:25.578940'),('l8ns3czfgkm1y8yq0p0o97c645xg2mfz','.eJxVjDsOwjAQBe_iGlmO4y8lPWewdtcbHEC2FCcV4u4QKQW0b2beSyTY1pK2zkuasziLKE6_GwI9uO4g36HemqRW12VGuSvyoF1eW-bn5XD_Dgr08q1BI2jC4JhyCEF5YjuqaD2YOFoXI_rBI48UTA6T9gNEjRMiWkuojBPvD_A8OBc:1uGlqc:sND1CDAZNpGxqgLeHmuYpHaZPUj2kfvH3Sfm6lBe4kk','2025-06-01 21:47:06.576214'),('oa2078domsxv1akcfqzej81jvgjbi1ad','.eJxVjEEOwiAQRe_C2pApUgGX7j0DmWEGqRpISrsy3l2bdKHb_977LxVxXUpcu8xxYnVWVh1-N8L0kLoBvmO9NZ1aXeaJ9KbonXZ9bSzPy-7-HRTs5VuTG6yY4ZhOATxkCTkbZJ8SA5FkGt2IiCScATKxTcFbZ1AAAlgbjHp_ABINOOU:1uPlue:o6tnYWbfjCbpBZwm4WXAsinxZrPd0HNWyx6tJZ6en-k','2025-06-26 17:40:28.245481');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-12 22:07:49
