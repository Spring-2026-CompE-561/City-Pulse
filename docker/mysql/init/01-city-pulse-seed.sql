-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: city_pulse
-- ------------------------------------------------------
-- Server version	8.0.45

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
-- Current Database: `city_pulse`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `city_pulse` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `city_pulse`;

--
-- Table structure for table `event_attending`
--

DROP TABLE IF EXISTS `event_attending`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_attending` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `event_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_event_attending_user_event` (`user_id`,`event_id`),
  KEY `ix_event_attending_user_id` (`user_id`),
  KEY `ix_event_attending_event_id` (`event_id`),
  CONSTRAINT `event_attending_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `event_attending_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_attending`
--

LOCK TABLES `event_attending` WRITE;
/*!40000 ALTER TABLE `event_attending` DISABLE KEYS */;
INSERT INTO `event_attending` VALUES (2,1,34);
/*!40000 ALTER TABLE `event_attending` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_comments`
--

DROP TABLE IF EXISTS `event_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `event_id` int NOT NULL,
  `text` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `ix_event_comments_event_id` (`event_id`),
  KEY `ix_event_comments_user_id` (`user_id`),
  CONSTRAINT `event_comments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `event_comments_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_comments`
--

LOCK TABLES `event_comments` WRITE;
/*!40000 ALTER TABLE `event_comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `event_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_likes`
--

DROP TABLE IF EXISTS `event_likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_likes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `event_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_event_like_user_event` (`user_id`,`event_id`),
  KEY `ix_event_likes_event_id` (`event_id`),
  KEY `ix_event_likes_user_id` (`user_id`),
  CONSTRAINT `event_likes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `event_likes_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_likes`
--

LOCK TABLES `event_likes` WRITE;
/*!40000 ALTER TABLE `event_likes` DISABLE KEYS */;
/*!40000 ALTER TABLE `event_likes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `region_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `title` varchar(512) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `category` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Technology',
  `source_id` int DEFAULT NULL,
  `origin_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'user',
  `external_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `external_url` varchar(2048) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `canonical_url` varchar(2048) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `event_start_at` datetime DEFAULT NULL,
  `event_end_at` datetime DEFAULT NULL,
  `timezone` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'America/Los_Angeles',
  `venue_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `venue_address` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `neighborhood` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'San Diego',
  `price_info` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `promo_summary` varchar(1024) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tags_json` text COLLATE utf8mb4_unicode_ci,
  `source_confidence` double DEFAULT NULL,
  `last_seen_at` datetime DEFAULT NULL,
  `event_image_url` varchar(2048) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_event_source_external` (`source_id`,`external_id`),
  UNIQUE KEY `uq_event_canonical_url` (`canonical_url`(512)),
  KEY `ix_events_user_id` (`user_id`),
  KEY `ix_events_region_id` (`region_id`),
  KEY `ix_events_source_id` (`source_id`),
  KEY `ix_events_neighborhood` (`neighborhood`),
  KEY `ix_events_city` (`city`),
  KEY `ix_events_event_start_at` (`event_start_at`),
  CONSTRAINT `events_ibfk_1` FOREIGN KEY (`region_id`) REFERENCES `regions` (`id`),
  CONSTRAINT `events_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_events_source` FOREIGN KEY (`source_id`) REFERENCES `sources` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
INSERT INTO `events` VALUES (5,0,NULL,'May 15, 2026 - PrimeTime Partner Meeting','Check-in & Refreshments: 9 am-9:15 am','2026-05-05 22:24:30','Community',7,'source','7-6435c0a41dc1d01a','https://www.eventbrite.com/e/may-15-2026-primetime-partner-meeting-tickets-1542749498279','https://www.eventbrite.com/e/may-15-2026-primetime-partner-meeting-tickets-1542749498279','2026-05-15 00:00:00','2026-05-15 00:00:00','America/Los_Angeles','Education Center',NULL,NULL,'San Diego','$0.99','dj; live music','{\"tags\": [], \"fingerprint\": \"2799bc8efc7ba984db0b3736e9414094f883655adf84b62b1b63acf7b2fd4657\", \"content_signature\": \"8330a93ff23e09cf24a030135245b727ddf16854cc0d661f32e34172d1e87359\", \"organizer_name\": \"SDUSD-ELO Department\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F983980353%2F125984588789%2F1%2Foriginal.20250314-165050?crop=focalpoint&fit=crop&w=512&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.443080558089&fp-y=0.308844561553&s=ff2cef6331c62bab51372064f0ea7c2c'),(6,0,NULL,'37th annual San Diego Crawfish Boil presented by LSU Alumni of San Diego','The World\'s Largest Crawfish Boil!','2026-05-05 22:24:30','Community',7,'source','7-7b6180871b08e6f9','https://www.eventbrite.com/e/37th-annual-san-diego-crawfish-boil-presented-by-lsu-alumni-of-san-diego-tickets-1976790364193','https://www.eventbrite.com/e/37th-annual-san-diego-crawfish-boil-presented-by-lsu-alumni-of-san-diego-tickets-1976790364193','2026-05-16 00:00:00','2026-05-16 00:00:00','America/Los_Angeles','Waterfront Park',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"968aa25234ff2088d988576ac243b3785319f5bbef13e8f0275a821c9e8937d4\", \"content_signature\": \"c7917243c2f790a4b80a009746b4caac5e355d349f6d81682fe8e589c0e67284\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1172294512%2F90601581453%2F1%2Foriginal.20251204-071130?crop=focalpoint&fit=crop&w=512&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.5&fp-y=0.5&s=331ccddf033e8d1a336c55db5beed895'),(7,0,NULL,'San Diego Career Fair','Connect live with Employers','2026-05-05 22:24:30','Community',7,'source','7-6c9de330f6e5c5e7','https://www.eventbrite.com/e/san-diego-career-fair-tickets-775251456977','https://www.eventbrite.com/e/san-diego-career-fair-tickets-775251456977','2026-05-18 00:00:00','2026-05-18 00:00:00','America/Los_Angeles','Hyatt Hotel',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"ecc2613f371b7256bdeb4333983d7eb777cba72012ea72e1e9fc433aa65405bd\", \"content_signature\": \"a50ee076f222e84ad71c0c41e313d1691d328bdf4c61276610b7a612b96a3d27\", \"organizer_name\": \"Career Fair Connection\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F656390479%2F316131771624%2F1%2Foriginal.20231210-233237?w=512&auto=format%2Ccompress&q=75&sharp=10&rect=0%2C15%2C1200%2C600&s=e5cd2d967db3a7e38d5d33e7069a7ee7'),(8,0,NULL,'San Diego Singles Mixer at Lionfish','Single in San Diego? Consider this your sign. Join us at Lionfish on Thursday, May 7 from 7–9PM for a singles mixer!','2026-05-05 22:24:30','Community',7,'source','7-8fc2bf0505c0c4c4','https://www.eventbrite.com/e/san-diego-singles-mixer-at-lionfish-tickets-1987961669869','https://www.eventbrite.com/e/san-diego-singles-mixer-at-lionfish-tickets-1987961669869','2026-05-07 00:00:00','2026-05-07 00:00:00','America/Los_Angeles','Lionfish Modern Coastal Cuisine – San Diego',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"6876e59bb9dba6adaed5477323d8b6a5e1ec991429d3292edd50125c3e4b96de\", \"content_signature\": \"1d4e5d60aad55060cbbbfebbdb564771ab3ab9033a6df9cd77f070f534e47ba4\", \"organizer_name\": \"Lionfish Modern Coastal Cuisine\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1182723745%2F174095885802%2F1%2Foriginal.20260421-213405?crop=focalpoint&fit=crop&w=512&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.481&fp-y=0.218&s=4c48fd425dfecea238642f67b2189546'),(9,0,NULL,'BURNHAM COMMUNITY DIALOGUE: The State of Our Community Fabric-OneSD Kickoff','Join the OneSD Kickoff: a public dialogue, baseline report highlights, and a vibrant community reception on May 12 at UCSD Park & Market','2026-05-05 22:24:30','Community',7,'source','7-ccf5bde3a50628ca','https://www.eventbrite.com/e/burnham-community-dialogue-the-state-of-our-community-fabric-onesd-kickoff-tickets-1987073074055','https://www.eventbrite.com/e/burnham-community-dialogue-the-state-of-our-community-fabric-onesd-kickoff-tickets-1987073074055','2026-05-12 00:00:00','2026-05-12 00:00:00','America/Los_Angeles','UC San Diego Park & Market',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"7040de7a526f8d1491e23a636124357d7ce5db3e24fdee258963fd138c249cc4\", \"content_signature\": \"b971abb1d237f68c5a4ebc112f393e502ac84e5c1e199a3055bbd6c892746a5d\", \"organizer_name\": \"Burnham Center for Community Advancement\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1181806260%2F780138296023%2F1%2Foriginal.20260409-180145?crop=focalpoint&fit=crop&w=306&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.5&fp-y=0.5&s=c459d72c35cd4ada07a8a6bf1c670c07'),(10,0,NULL,'23rd Annual \"Innovation in Education Awards Program\"','The premiere awards event in San Diego County that honors educators and students for their innovative achievements','2026-05-05 22:24:30','Community',7,'source','7-9dda2b043e8fac3a','https://www.eventbrite.com/e/23rd-annual-innovation-in-education-awards-program-tickets-1860535855829','https://www.eventbrite.com/e/23rd-annual-innovation-in-education-awards-program-tickets-1860535855829','2026-05-14 00:00:00','2026-05-14 00:00:00','America/Los_Angeles','SeaWorld San Diego',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"ab765624f20b5ff9f2522b774c8e6972d4f30a044489507ac94a282ac5a6e36c\", \"content_signature\": \"776041ffc65d3fe90ecb9dcf63a70d59e698df3dfc3c766da5d93c08e68a6d2a\", \"organizer_name\": \"Classroom of the Future Foundation\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1181848400%2F487860612289%2F1%2Foriginal.20260410-064114?crop=focalpoint&fit=crop&w=512&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.04&fp-y=0.308&s=b187793c2e935950ce272d61c9d3c0fb'),(11,0,NULL,'Molly\'s Angels 2026 San Diego Tennis Fest','Come join us for a day filled with tennis excitement! Whether you\'re a seasoned player or just starting out, this event is for all levels','2026-05-05 22:24:30','Community',7,'source','7-08c69a0e695d268b','https://www.eventbrite.com/e/mollys-angels-2026-san-diego-tennis-fest-tickets-1986491291929','https://www.eventbrite.com/e/mollys-angels-2026-san-diego-tennis-fest-tickets-1986491291929','2026-05-17 00:00:00','2026-05-17 00:00:00','America/Los_Angeles','Balboa Tennis Club',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"e6521bbbeff413f2e6cbabb97d7eec493b9f626ffeec9ff7944a33da966cd37b\", \"content_signature\": \"6827ab6c7e387c8a744d1088198eaaec940af2992ac3b27f12a1722bbef37cd8\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1181633345%2F3387390908%2F1%2Foriginal.20260407-202510?crop=focalpoint&fit=crop&w=512&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.136&fp-y=0.139&s=9952b566a9530319e756e6b542ea5446'),(12,0,NULL,'MCASD x Future is Color Presents: Jazz Night','Join Future is Color and the Museum of Contemporary Art San Diego for our quarterly jazz night hosted in MCASD\'s Art Park','2026-05-05 22:24:30','Community',7,'source','7-c8b6f61def1b9564','https://www.eventbrite.com/e/mcasd-x-future-is-color-presents-jazz-night-tickets-1985839016957','https://www.eventbrite.com/e/mcasd-x-future-is-color-presents-jazz-night-tickets-1985839016957','2026-05-21 00:00:00','2026-05-21 00:00:00','America/Los_Angeles','Museum of Contemporary Art San Diego',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"82a6ffb23981e7322c7307669b56675f66ee45b31f35016794b6f0fe6115145d\", \"content_signature\": \"5da86b9a41365f0ccb3aa97f30c6821a891b5f2633eb12da9a7ad13b46a82169\", \"organizer_name\": \"Future Is Color\\u00ae\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1173729730%2F2318641324613%2F1%2Foriginal.20251230-205537?crop=focalpoint&fit=crop&w=512&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.5&fp-y=0.5&s=1ecd244678927ab19bbfb1a8ef1ea777'),(13,0,NULL,'The Basement Demo Day 2026','Join our signature year-end celebration ft. Blackstone LaunchPad student startups demos, i4x project posters, and pitch competition!','2026-05-05 22:24:30','Community',7,'source','7-aa2cc5e88249c38a','https://www.eventbrite.com/e/the-basement-demo-day-2026-tickets-1985946966838','https://www.eventbrite.com/e/the-basement-demo-day-2026-tickets-1985946966838','2026-05-21 00:00:00','2026-05-21 00:00:00','America/Los_Angeles','UC San Diego - Design and Innovation Building',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"2505b92609d1610d72006383b6c3cb8017e9d93bf989ff64f2780b9dd9597118\", \"content_signature\": \"7847af54dbe1358935347023e75fb8ede0407d211db611022a2b6baf952c2e6b\", \"organizer_name\": \"UC San Diego - The Basement\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1180711360%2F88812327741%2F1%2Foriginal.20260325-231333?crop=focalpoint&fit=crop&w=400&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.129&fp-y=0.494&s=073ff88a66191746dc7ae9a8511f8b25'),(14,0,NULL,'LOS MIRLOS (Legends of Cumbia), Tropa Magica, REZA','Bad Vibes Good Friends and Quartyard present: Los Mirlos, Tropa Magica, and REZA','2026-05-05 22:24:30','Community',7,'source','7-ebf22f5b0398e8f5','https://www.eventbrite.com/e/los-mirlos-legends-of-cumbia-tropa-magica-reza-tickets-1988433666624','https://www.eventbrite.com/e/los-mirlos-legends-of-cumbia-tropa-magica-reza-tickets-1988433666624','2026-05-28 00:00:00','2026-05-28 00:00:00','America/Los_Angeles','Quartyard',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"51fe63fcc2a00319494b47377baaad3b770805472326ac6d22da7b4cd4b8ce0e\", \"content_signature\": \"ecce1d08b372c2e82b98568cca9e28c85c46b7ade264dfc04f0c471556de0043\", \"organizer_name\": \"Quartyard\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1183261902%2F2558105767521%2F1%2Foriginal.20260428-192645?crop=focalpoint&fit=crop&w=512&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.5&fp-y=0.5&s=71c39d99c131f0b4e7c498152f8559c7'),(15,0,NULL,'Skills // Systemisch #2 / Van Zij naar Wij','Game Changers die in diverse contexten werkzaam zijn, krijgen de kans om hun vaardigheden verder te verdiepen en versterken','2026-05-05 22:24:30','Community',7,'source','7-5fc7d5f263ca3b03','https://www.eventbrite.nl/e/tickets-skills-systemisch-2-van-zij-naar-wij-1687607923729','https://www.eventbrite.nl/e/tickets-skills-systemisch-2-van-zij-naar-wij-1687607923729','2026-05-06 00:00:00','2026-05-06 00:00:00','America/Los_Angeles','Eventbrite San Diego Events',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"b47a96195515377d6e361744e458eb87b445effe23087cc99c5832c079a79d7a\", \"organizer_name\": \"number 5 foundation\"}',0.8,'2026-05-05 22:24:30','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1182674657%2F2883884284961%2F1%2Foriginal.20260421-141618?w=480&auto=format%2Ccompress&q=75&sharp=10&s=cae13652b1aed557486aab201359ac79'),(16,0,NULL,'How to Do a  Venture Capital Financing','The speaker will discuss how to do a venture capital financing','2026-05-05 22:24:30','Community',7,'source','7-330aa91ab9202af0','https://www.eventbrite.ca/e/how-to-do-a-venture-capital-financing-tickets-812165377507','https://www.eventbrite.ca/e/how-to-do-a-venture-capital-financing-tickets-812165377507','2026-05-14 00:00:00','2026-05-14 00:00:00','America/Los_Angeles','Eventbrite San Diego Events',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"12a20b8546ab169c1c5aab26bfb49c1b73444da0fa1861798fe100f4eccdf829\", \"content_signature\": \"fa038f27fe3fac38ed10bf3f632b33eb72e3e522ee3b04c6dfe430c2eb76dad1\", \"organizer_name\": \"Idea to IPO\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F485664049%2F3951017871%2F1%2Foriginal.20210122-000942?w=306&auto=format%2Ccompress&q=75&sharp=10&rect=4%2C0%2C306%2C153&s=ba5e43f03716796bdb9a171c845765cf'),(17,0,NULL,'Henry VII: Treason and Trust','Discover the story of one of England’s unlikeliest monarchs','2026-05-05 22:24:30','Community',7,'source','7-da74d57c8fb2f447','https://www.eventbrite.co.uk/e/henry-vii-treason-and-trust-tickets-1983072347775','https://www.eventbrite.co.uk/e/henry-vii-treason-and-trust-tickets-1983072347775','2026-05-15 00:00:00','2026-05-15 00:00:00','America/Los_Angeles','Eventbrite San Diego Events',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"298b6932f99f3eb631bf90300b22c93570b95db2cc9a23309d3e65fd4a059f05\", \"content_signature\": \"e2454c7319cf69051359817e4c0cee31d5b6151242cf67da82e429d9d13079ec\", \"organizer_name\": \"The National Archives\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1177719713%2F1375051228453%2F1%2Foriginal.20260217-131651?w=512&auto=format%2Ccompress&q=75&sharp=10&rect=0%2C663%2C2400%2C1200&s=ebb95a31024d359f64008ea1c87a686d'),(18,0,NULL,'The AI Edge: Supercharge Your Startup Vision','Get ready to level up your startup game with cutting-edge AI technology at The AI Edge event - it\'s time to supercharge your vision!','2026-05-05 22:24:30','Community',7,'source','7-80c4eb828f33b42d','https://www.eventbrite.com/e/the-ai-edge-supercharge-your-startup-vision-tickets-1425498467289','https://www.eventbrite.com/e/the-ai-edge-supercharge-your-startup-vision-tickets-1425498467289','2026-05-18 00:00:00','2026-05-18 00:00:00','America/Los_Angeles','Eventbrite San Diego Events',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"ef06aed90a35b6a7da0e991f0b9c3883274642a4d093dc70b7aee5521269c2a2\", \"content_signature\": \"1316fcac71b0c8cbaea54b553aa4f81caa2a46a4989d4b05dcfae233f4131853\", \"organizer_name\": \"Silicon Networks\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1057869583%2F330415169387%2F1%2Foriginal.png?w=512&auto=format%2Ccompress&q=75&sharp=10&rect=0%2C0%2C940%2C470&s=8956d668588828669ae360a81efd0582'),(19,0,NULL,'Webinar: Alles over BTW voor dansscholen en -groepen','Wat verandert er in 2026 in de btw-regeling en wat is de impact op dansscholen en -groepen?','2026-05-05 22:24:30','Community',7,'source','7-397a58128d1dc829','https://www.eventbrite.be/e/tickets-webinar-alles-over-btw-voor-dansscholen-en-groepen-1982959838256','https://www.eventbrite.be/e/tickets-webinar-alles-over-btw-voor-dansscholen-en-groepen-1982959838256','2026-05-19 00:00:00','2026-05-19 00:00:00','America/Los_Angeles','Eventbrite San Diego Events',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"65508cd009e5ec8987708c0b589b33d347906b3d22f28a6b599e175b3efe0ff9\", \"organizer_name\": \"Danspunt vzw\"}',0.8,'2026-05-05 22:24:30','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1177363892%2F266028117055%2F1%2Foriginal.20260212-111628?w=480&auto=format%2Ccompress&q=75&sharp=10&rect=0%2C281%2C2048%2C1024&s=c86533a3b6db82a87ff21f1876ca478d'),(20,0,NULL,'Bakersfield Career Fair','Connect with Bakersfield Employers','2026-05-05 22:24:30','Community',7,'source','7-2557ba03078bda5e','https://www.eventbrite.com/e/bakersfield-career-fair-tickets-295406437607','https://www.eventbrite.com/e/bakersfield-career-fair-tickets-295406437607','2026-05-27 00:00:00','2026-05-27 00:00:00','America/Los_Angeles','Eventbrite San Diego Events',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"99a38674f576e25825aa7638490b10d97c5152d3e86ba84317cd92056d26481c\", \"content_signature\": \"200f7bcfcf1cac9368a581ecf604323fa89db62149eca7062fc50134dd09c94b\", \"organizer_name\": \"Career Fair Connection\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F683466719%2F316131771624%2F1%2Foriginal.20240126-171826?w=464&auto=format%2Ccompress&q=75&sharp=10&rect=76%2C0%2C464%2C232&s=7fd76b818dd84e4a331f96ff90b3f2c1'),(21,0,NULL,'Vincent Neil Emerson: Blue Stars Tour','Presented by Soda Bar','2026-05-05 22:24:31','Community',7,'source','7-6a2d4b5cc8380b67','https://www.eventbrite.com/e/vincent-neil-emerson-blue-stars-tour-tickets-1981633891313','https://www.eventbrite.com/e/vincent-neil-emerson-blue-stars-tour-tickets-1981633891313','2026-05-08 00:00:00','2026-05-08 00:00:00','America/Los_Angeles','Quartyard',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"a7fa1ee81d82241d7a79a70d2750b7af7cde1e72ec19d43e59358cb2f81dde5b\", \"content_signature\": \"8417364944d36010a054c4f56a245f15dde955744cbaa8e52d3d790b5c031fbc\", \"organizer_name\": \"Quartyard\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1175899972%2F2558105767521%2F1%2Foriginal.20260126-235359?crop=focalpoint&fit=crop&w=400&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.499&fp-y=0.074&s=2cb66f57abf16e29374ac7562c0e1f47'),(22,0,NULL,'Pasta Making With Chef Adriana at a Local Brewery - Pasta Making Cooking Class in San Diego | Classpop!™','Pasta Making With Chef Adriana at a Local Brewery - Pasta Making Cooking Class in San Diego | Classpop!™ is happening at Mission Brewing - Downtown in San Diego','2026-05-05 22:24:31','Community',7,'source','7-91929944644f9099','https://www.eventbrite.com/e/pasta-making-with-chef-adriana-at-a-local-brewery-pasta-making-cooking-class-in-san-diego-classpoptm-tickets-1983792261055','https://www.eventbrite.com/e/pasta-making-with-chef-adriana-at-a-local-brewery-pasta-making-cooking-class-in-san-diego-classpoptm-tickets-1983792261055','2026-05-08 00:00:00','2026-05-08 00:00:00','America/Los_Angeles','Mission Brewing - Downtown',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"5d3d50bf56707c17cd998ecfd92205c6392bf65ea533dcdc74e178a17e9f744e\", \"content_signature\": \"e5e5d7e2e9d32d4e5c7b02e5f24e8286fbb61756b67e6f8bb583be6bf612b0f2\", \"organizer_name\": \"Classpop!\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1173164293%2F316402407909%2F1%2Foriginal.20251217-214648?w=400&auto=format%2Ccompress&q=75&sharp=10&s=c317ccc4c5d1e1b4ae42b8b204ad6a95'),(23,0,NULL,'North Park Plant Sale','Flowers, succulents, cacti, air plants, herbs and other edibles, planting station, workshops, and plant-inspired art','2026-05-05 22:24:31','Community',7,'source','7-306cc58e57f420b6','https://www.eventbrite.com/e/north-park-plant-sale-tickets-1977481242629','https://www.eventbrite.com/e/north-park-plant-sale-tickets-1977481242629','2026-05-09 00:00:00','2026-05-09 00:00:00','America/Los_Angeles','North Park Mini Park',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"2953fff5bd8a6afee11113c4aaa04886207ab3f34bd027a0026cae6911645d43\", \"content_signature\": \"3feb34813854675cb558da4d5d0a3d3f5019fe7ea7193edc11f47594ed0d3de8\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F962212153%2F349512467209%2F1%2Foriginal.20250217-081226?crop=focalpoint&fit=crop&w=512&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.346502590674&fp-y=0.867704280156&s=f55cb2143d1bd2350d3d70e27f873745'),(24,0,NULL,'RIK JAM - Live @ The Harp Ocean Beach','Rik Jam is well-known for his distinctive fusion of Reggaeton and other Latin genres','2026-05-05 22:24:31','Community',7,'source','7-5a8bd046d2b0b036','https://www.eventbrite.com/e/rik-jam-live-the-harp-ocean-beach-tickets-1983273257702','https://www.eventbrite.com/e/rik-jam-live-the-harp-ocean-beach-tickets-1983273257702','2026-05-09 00:00:00','2026-05-09 00:00:00','America/Los_Angeles','The Harp',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"c9d8e6f335805cafdf50d66dd859f9154d7362a5f010084bea6ed356e17a8824\", \"content_signature\": \"0bc10b08a2cbb3215af7632f9d451271c024dbf42a68dbb323aae4dfb61852b4\", \"organizer_name\": \"The Harp Ocean Beach\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1182104803%2F2990893153052%2F1%2Foriginal.20260414-043608?crop=focalpoint&fit=crop&w=400&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.52&fp-y=0.039&s=dbe9735d00471d19ebeba7fee948f2a2'),(25,0,NULL,'Daft Disko: San Diego','Daft Disko makes its San Diego debut!','2026-05-05 22:24:31','Community',7,'source','7-c0f2110457b7e72b','https://www.eventbrite.com/e/daft-disko-san-diego-tickets-1984437172001','https://www.eventbrite.com/e/daft-disko-san-diego-tickets-1984437172001','2026-05-09 00:00:00','2026-05-10 00:00:00','America/Los_Angeles','Phantom Lounge and Nightclub',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"291cdf2c08f67fad084c45f33f448e6832086a4c8d1e1f1ce65621c80dc30325\", \"content_signature\": \"a8e4c58b816febe51960006817405f8f1022366fcdd97ec5c2e902ae3ab10883\", \"organizer_name\": \"ORLOVE\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1178966528%2F290918113901%2F1%2Foriginal.20260304-003640?crop=focalpoint&fit=crop&w=512&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.051&fp-y=0.543&s=d0ca2dca85043a6ccc64bfda678e7009'),(26,0,NULL,'Song, Story, Stage | USD S3 Ensemble','Students in Song/Story/Stage: A Music and Theatre Ensemble present a concert of scenes from musical theatre','2026-05-05 22:24:31','Community',7,'source','7-67addef193eba76c','https://www.eventbrite.com/e/song-story-stage-usd-s3-ensemble-tickets-1981375815401','https://www.eventbrite.com/e/song-story-stage-usd-s3-ensemble-tickets-1981375815401','2026-05-09 00:00:00','2026-05-09 00:00:00','America/Los_Angeles','Studio Theatre, Sacred Heart Hall',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"e1951e927c469b9f2ddb59988e984f34196cc7b396f047f9096c20b5b7691414\", \"content_signature\": \"cdfe289c3ea38c993f17e0bd8ca6461ab82fbc0063e2fac5c407f1ba5befd4b0\", \"organizer_name\": \"University of San Diego Department of Music\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1175591650%2F131690905339%2F1%2Foriginal.20260122-204817?crop=focalpoint&fit=crop&w=512&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.5&fp-y=0.5&s=75f7407e46e4a13b4f7c1e65d872f7d3'),(27,0,NULL,'Patchwork Mother\'s Day Air Plant Wreaths Craft Workshop','Sip, Style & Celebrate Mom','2026-05-05 22:24:31','Community',7,'source','7-9697b6de7de0da8b','https://www.eventbrite.com/e/patchwork-mothers-day-air-plant-wreaths-craft-workshop-tickets-1984486324016','https://www.eventbrite.com/e/patchwork-mothers-day-air-plant-wreaths-craft-workshop-tickets-1984486324016','2026-05-10 00:00:00','2026-05-10 00:00:00','America/Los_Angeles','Liberty Station NTC Park',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"2dd6c429bc64a0a43b35846d2f5c5e7d92b6dbb3d1a49eb25184422f68fdf174\", \"content_signature\": \"2e0f7250bebfabbec0a86cab531a350994a15416a991924105dbaec364366971\", \"organizer_name\": \"Patchwork\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F730158949%2F259501907147%2F1%2Foriginal.20240328-005438?w=512&auto=format%2Ccompress&q=75&sharp=10&rect=0%2C0%2C2160%2C1080&s=ccd767ec05b42cede5eef138773e5d91'),(28,0,NULL,'#SUNDAY 7:00 PM','The best way to ease into another week is with a Sunday night of comedy!','2026-05-05 22:24:31','Community',7,'source','7-ec7cbbf2fd802944','https://www.eventbrite.com/e/sunday-700-pm-tickets-1984334775731','https://www.eventbrite.com/e/sunday-700-pm-tickets-1984334775731','2026-05-10 00:00:00','2026-05-10 00:00:00','America/Los_Angeles','Laugh Factory',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"52edfbc621b02e3ec3bf3684f8c32f1e692256608153799c5cef3e6e872f694f\", \"content_signature\": \"35d731a1e239868f42bdacd7c5418c346aed0b4fda660b89f5717eb4f2af183a\", \"organizer_name\": \"Laugh Factory - San Diego\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1183861193%2F2987014365277%2F1%2Foriginal.20260505-213645?w=400&auto=format%2Ccompress&q=75&sharp=10&s=bc75f370736245940d30adfa0fc3fecf'),(29,0,NULL,'Eric Johnson - Texaphonic Tour 2026','Eric Johnson - Texaphonic Tour 2026 is happening at House of Blues San Diego in San Diego','2026-05-05 22:24:35','Nightlife',2,'source','2-bd7674e5fd7e86fb','https://sandiego.houseofblues.com/shows','https://sandiego.houseofblues.com/shows','2026-05-07 02:00:00',NULL,'America/Los_Angeles','House of Blues San Diego',NULL,'Gaslamp','San Diego','$1, $2, $14','dj','{\"tags\": [\"dj\"], \"fingerprint\": \"89d0912fcecde8ac4d3065f3411ed109c2a6e74fdaa87bc78f34635fca68c004\", \"content_signature\": \"a88281cd79ad3c78d199566d0954b1d5a09c1c1455c8851f8ba78b6bd7f80a6b\"}',0.82,'2026-05-05 22:41:03','https://s1.ticketm.net/dam/a/403/f3293d88-8d43-440d-8dcb-4f74dcbe2403_TABLET_LANDSCAPE_LARGE_16_9.jpg'),(30,0,NULL,'Ashley Kutcher','Ashley Kutcher is happening at House of Blues San Diego in San Diego','2026-05-05 22:24:35','Nightlife',2,'source','2-a992ccf1f816c81d','https://sandiego.houseofblues.com/shows/rooms/voodoo-room','https://sandiego.houseofblues.com/shows/rooms/voodoo-room','2026-05-09 02:00:00',NULL,'America/Los_Angeles','House of Blues San Diego',NULL,'Gaslamp','San Diego','$1, $2, $6','dj','{\"tags\": [\"dj\"], \"fingerprint\": \"7aacbae33461bc4ee7b8b23c7561c7de0f235f1e8cf22f1df5e8e21e79b1caee\", \"content_signature\": \"9da19677f155f0aecead8f29225c3e11f668d16b8e9234b96f0f2209745b419c\"}',0.82,'2026-05-05 22:41:03','https://s1.ticketm.net/dam/a/50e/41502b27-ae1e-443a-9dbb-2ad68cd0e50e_TABLET_LANDSCAPE_LARGE_16_9.jpg'),(31,0,NULL,'LOVE HANGOVER DANCE PARTY','Queer * Punk * Acid * Sweat','2026-05-05 22:25:17','Music',11,'source','11-5b34a86e77912047','https://whistlestopbar.com/event/love-hangover-dance-party-6','https://whistlestopbar.com/event/love-hangover-dance-party-6','2026-05-08 04:00:00','2026-05-08 04:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego','$1, $15','dj; happy hour','{\"tags\": [], \"fingerprint\": \"b29978f010a005dcd41b5e1b7d4156c16896eee13175615fc2fcff00cdfd0af2\", \"content_signature\": \"0819f47fc7d49d704fa4a17364e5a991723006237ec291cbb1ed95ac2ac202e5\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:06','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(32,0,NULL,'Total Wife, Misfire, Neutral Shirt','Total Wife, Misfire, Neutral Shirt is happening at Whistle Stop Events in San Diego','2026-05-05 22:25:17','Music',11,'source','11-8bd6c56e5a97f8a3','https://whistlestopbar.com/event/total-wife-misfire','https://whistlestopbar.com/event/total-wife-misfire','2026-05-09 04:00:00','2026-05-09 04:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"ddf48ec0caf994a404cb1d42076841448c2b3006c8502945bbc932d1871afb14\", \"content_signature\": \"fdd5f642d59660de85513204b4c4372f657c162880042f5258bda88ee0f2c17a\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(33,0,NULL,'Saturday Afternoon Fever w/DJ Krys Da Cat','Saturday Afternoon Fever w/DJ Krys Da Cat is happening at Whistle Stop Events in San Diego','2026-05-05 22:25:17','Music',11,'source','11-6ce3361bee16a47e','https://whistlestopbar.com/event/saturday-afternoon-fever-w-dj-krys-da-cat-18','https://whistlestopbar.com/event/saturday-afternoon-fever-w-dj-krys-da-cat-18','2026-05-09 23:00:00','2026-05-09 23:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"e434c33cf7a60916752fbd42b5526ef8cdc26cac08011a81ad2e53d52ce0a2de\", \"content_signature\": \"6f45721dea520a7df0173b531d4611767d57e8704d8f1873b349ae301db1f93c\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(34,0,NULL,'BOOTY BASSMENT w/DJ Dimitri, Rob Moran, and Guests $15','DJ Dimitri and Rob Moran host the one and only Booty Bassment - San Diego’s longest running hip hop dance party - 20 years strong! Check the vibe - every 2nd, 4th (and 5th) Saturday nights at Whistle Stop Bar','2026-05-05 22:25:17','Music',11,'source','11-6d982c462a15f9e6','https://whistlestopbar.com/event/booty-bassment-w-dj-dimitri-rob-moran-and-guests-15-42','https://whistlestopbar.com/event/booty-bassment-w-dj-dimitri-rob-moran-and-guests-15-42','2026-05-10 04:00:00','2026-05-10 04:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"8c3c048edb8f6bb5008736d3c9e2e9afc82c16d3b3c91d1f75abfc83c9de5a43\", \"content_signature\": \"cb43835d46756db4ae455cc789755a588f5240a05feeb0b990005ccaac30826e\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(35,0,NULL,'Showdown at Sundown','The Sheriff’s Monthly Country Music Happy Hour…every Second Sunday!! Saddle up!! 5-8 PM 🪕🤠🎻','2026-05-05 22:25:17','Music',11,'source','11-b3553aef3867a0f0','https://whistlestopbar.com/event/showdown-at-sundown-40','https://whistlestopbar.com/event/showdown-at-sundown-40','2026-05-10 23:00:00','2026-05-10 23:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"7e1bf57e1187fc7d3ccd4761ae6535d296854834ebbc1f74aea3e71060c2136a\", \"content_signature\": \"5a47b7681d619c5b9bba175fc3fed6ef8ff9de8ca0b1d99c13acbdf1a4c48531\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(36,0,NULL,'Showdown at Sundown','The Sheriff’s Monthly Country Music Happy Hour…every Second Sunday!! Saddle up!! 5-8 PM 🪕🤠🎻','2026-05-05 22:25:17','Music',11,'source','11-018d03b25d077ef3','https://whistlestopbar.com/event/showdown-at-sundown-18','https://whistlestopbar.com/event/showdown-at-sundown-18','2026-05-11 00:00:00','2026-05-11 00:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"34d98e487274720341a66f3d2c5e13ff9bd4730c7434aa005234f9552fc7b174\", \"content_signature\": \"bb5430f49a38f7155679a827ea28e53386bf9c8da9226792f0c1657ab2648c11\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(37,0,NULL,'Friday Happy Hour w/ DJ Shoeshine','Friday Happy Hour w/ DJ Shoeshine is happening at Whistle Stop Events in San Diego','2026-05-05 22:25:17','Music',11,'source','11-bfb6ce4ccdb2f752','https://whistlestopbar.com/event/friday-happy-hour-w-dj-shoeshine-37','https://whistlestopbar.com/event/friday-happy-hour-w-dj-shoeshine-37','2026-05-16 00:00:00','2026-05-16 03:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"985b2a3727b2fc5c7e253cc9568bc83b80a6b2efa63e4939c1164d1462b13f0d\", \"content_signature\": \"cbf6b914eaab9ebfb20c875f071841dafa22ac5869da7103fb977335102adb36\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(38,0,NULL,'F#!KIN’ IN THE BUSHES','DJ Daniel Sant brings the bangers for his Brit Pop, Post-Punk and Madchester Dance Party, every 3rd Friday at Whistle Stop! 🕺🏻🎧 Dance the night away! / Hang the DJ!!','2026-05-05 22:25:17','Music',11,'source','11-c35483a4c1c9ab18','https://whistlestopbar.com/event/fkin-in-the-bushes-19','https://whistlestopbar.com/event/fkin-in-the-bushes-19','2026-05-16 04:00:00','2026-05-16 04:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"f12069ab5adc5bfa6f3f77a62c7a11d559399f3b8e4dd443b427774635beb971\", \"content_signature\": \"14f7610b2fdcc8786a2df2613f9e8c87a0092f55402b7f81f0090a733e2b9bb9\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(39,0,NULL,'Vinyl Junkies DJ Happy Hour!','Our friends/neighbors/favorite record store join us for this monthly offering featuring various members of the Vinyl Junkies staff! Every third Saturday, 5-8pm. FREE! 🧑🏼‍🎤','2026-05-05 22:25:17','Music',11,'source','11-76927d12704d0f6b','https://whistlestopbar.com/event/vinyl-junkies-dj-happy-hour-19','https://whistlestopbar.com/event/vinyl-junkies-dj-happy-hour-19','2026-05-17 00:00:00','2026-05-17 03:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"c0c7220ec5e8c05f1ee456bc05402867d62b44a495e318dccda1fa438183c9c0\", \"content_signature\": \"cb90b2ade5285132ae9992e403c3fd2dad22a0ce77cc722fa925f1e96015410a\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(40,0,NULL,'80s vs 90s vs Y2K! with DJ Gabe Vega and Guests','San Diego’s Best Mix of Eclectic Dance Jams from the 80s, 90, and 2000s!! DJ Gabe Vega leads this dance party at Whistle Stop Bar, every 1st and 3rd Saturday night! 🪩','2026-05-05 22:25:17','Music',11,'source','11-e47f4f61cc6b7980','https://whistlestopbar.com/event/80s-vs-90s-vs-y2k-with-dj-gabe-vega-and-guests-19','https://whistlestopbar.com/event/80s-vs-90s-vs-y2k-with-dj-gabe-vega-and-guests-19','2026-05-17 04:00:00','2026-05-17 04:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"0fcd61166cbd71818fe1248fcefaf8a03701f03932afc5251f1e22928ce9ef00\", \"content_signature\": \"d12bab1627408abb4c91c7571206f2b758873a1deeecd37d71be36d1b23abc2d\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(41,0,NULL,'GODSHELL, RX.PINKNOISE, BREADTH','GODSHELL, RX.PINKNOISE, BREADTH is happening at Whistle Stop Events in San Diego','2026-05-05 22:25:17','Music',11,'source','11-c0ab7c8ce38aa25a','https://whistlestopbar.com/event/godshell-rx-pink-noise-breadth','https://whistlestopbar.com/event/godshell-rx-pink-noise-breadth','2026-05-20 04:00:00','2026-05-20 04:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"16ae2dd507e52c2414ee3bd813fcd0ac06b9b0820c6711e669dcb31fe54fb6a9\", \"content_signature\": \"b2cbf8f3c290e2b46a766b34d9a03552ce7270971e0c58e03bb5a3ab3e80dc55\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(42,0,NULL,'GIANT WASTE OF MAN, RICKY','+DJ FAT EARTHER | FREE SHOW!','2026-05-05 22:25:17','Music',11,'source','11-4685c3a5844da07c','https://whistlestopbar.com/event/giant-waste-of-man-ricky','https://whistlestopbar.com/event/giant-waste-of-man-ricky','2026-05-21 04:00:00','2026-05-21 04:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"245b5abad31312945d05049f64e064a1a6123a820441a322252e460252f8070d\", \"content_signature\": \"6485109ff1573ce48c5cd22875e67aa6633831babe0f1e34ded9c0927064bb20\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(43,0,NULL,'Caralee, Blood Handsome','Caralee, Blood Handsome is happening at Whistle Stop Events in San Diego','2026-05-05 22:25:17','Music',11,'source','11-91d76a6bde4f4568','https://whistlestopbar.com/event/caralee-blood-handsome','https://whistlestopbar.com/event/caralee-blood-handsome','2026-05-22 04:00:00','2026-05-22 04:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"c4b3a98129eeabca6f1d97e2a58eb826e8dcde864aa2f9f24d64ae8ac721a27c\", \"content_signature\": \"b456fb8021207945f28f0aaf14a6a262d4b3951776c29ad79f97ff1719d48052\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(44,0,NULL,'MADELINE GOLDSTEIN, MORE EPHEMEROL','MADELINE GOLDSTEIN, MORE EPHEMEROL is happening at Whistle Stop Events in San Diego','2026-05-05 22:25:17','Music',11,'source','11-382c3f13ecc600fb','https://whistlestopbar.com/event/madeline-goldstein-more-ephemerol','https://whistlestopbar.com/event/madeline-goldstein-more-ephemerol','2026-05-23 04:00:00','2026-05-23 04:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"5ae988635d69f49ced3dce5986d41d000eabb619deeba8e8e3fd2277891373aa\", \"content_signature\": \"3563ff7dacd7356be64b07d07efc4b51559905958978f6054c59da98b9c095a5\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(45,0,NULL,'THE AMANDAS MATINEE SHOW','THE AMANDAS MATINEE SHOW is happening at Whistle Stop Events in San Diego','2026-05-05 22:25:17','Music',11,'source','11-4b802e951bc32227','https://whistlestopbar.com/event/the-amandas-matinee-show','https://whistlestopbar.com/event/the-amandas-matinee-show','2026-05-23 23:00:00','2026-05-23 23:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"1b7ad12aca705dcac010f18ddf96bf9f26ffe25ba94d17779bd3a4d28ea14870\", \"content_signature\": \"754e8783570c0b26c3bff90b10c28ed5fddc76621dfc02a94fec892094612628\", \"organizer_name\": null}',0.8,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(46,0,NULL,'Past Events from November 29, 2024 &#8211; November 14, 2024 &#8211; Whistle Stop Bar','Past Events from November 29, 2024 – November 14, 2024 – Whistle Stop Bar is happening at Whistle Stop Events in San Diego','2026-05-05 22:25:17','Music',11,'source','11-203d769a5b5e1aec','https://whistlestopbar.com/events/list?eventDisplay=past','https://whistlestopbar.com/events/list?eventDisplay=past','2026-05-20 00:00:00',NULL,'America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego','$1, $15','dj; happy hour','{\"tags\": [\"dj\", \"happy hour\"], \"fingerprint\": \"00f4813d6553978ad2cc749bef9f7c03c0ad6e2ee8410e0907679a95e50f2d13\", \"content_signature\": \"30672106baba8bdae7e6336cb749f03146f3bb16030430f08c927528db06370b\", \"organizer_name\": null}',0.65,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(47,0,NULL,'BOOTY BASSMENT w/DJ Dimitri, Rob Moran, and Guests $15','DJ Dimitri and Rob Moran host the one and only Booty Bassment - San Diego’s longest running hip hop dance party - 20 years strong! Check the vibe - every […]','2026-05-05 22:25:17','Music',11,'source','11-d5b1cf3f7a236683','https://whistlestopbar.com/events/list/page/2','https://whistlestopbar.com/events/list/page/2','2026-05-24 04:00:00','2026-05-24 04:00:00','America/Los_Angeles','Whistle Stop Events',NULL,'South Park','San Diego','$1, $15','dj; happy hour','{\"tags\": [\"dj\", \"happy hour\"], \"fingerprint\": \"c22db4d46021caec10aeea66634a2a6cd088b53200a09008c60743dc01981601\", \"content_signature\": \"9bd176d181773fbcac734f2102beeb4c12f8f4c75a23b1c0bdbb8859bff86b2e\", \"organizer_name\": null}',0.82,'2026-05-05 22:42:07','https://whistlestopbar.com/wp-content/uploads/2024/11/cropped-whistle_logo.png'),(48,0,NULL,'Last royals of the Punjab: The Duleep Singhs (online)','Last royals of the Punjab: The Duleep Singhs (online) is happening at Eventbrite San Diego Events in San Diego.','2026-05-05 22:35:08','Community',7,'source','7-802b5da49e201a2c','https://www.eventbrite.co.uk/e/last-royals-of-the-punjab-the-duleep-singhs-online-tickets-1982185586448','https://www.eventbrite.co.uk/e/last-royals-of-the-punjab-the-duleep-singhs-online-tickets-1982185586448','2026-05-06 00:00:00','2026-05-06 00:00:00','America/Los_Angeles','Eventbrite San Diego Events',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"ce6732eb78291eaf9cee8f8fdca7e1ae3b767b87d9152db93b765fdfced57c8e\", \"content_signature\": \"a1599c08541621899e235d9e98b8836b08b34ddebea6c4054bc40095472e5d0b\", \"organizer_name\": \"Norfolk Record Office\"}',0.8,'2026-05-05 22:35:08','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1176445675%2F67908995559%2F1%2Foriginal.20260202-132503?w=480&auto=format%2Ccompress&q=75&sharp=10&rect=0%2C298%2C2524%2C1262&s=cdfd8bfc90a61b187120eca603622ec9'),(49,0,NULL,'Emirates Connect | B2B Networking | SMEs & Startups','Connect. Collaborate. Grow. Dubai’s Weekly Meet-Up for SMEs & Startups','2026-05-05 22:35:08','Community',7,'source','7-e7e0e3f3930eb213','https://www.eventbrite.com/e/emirates-connect-b2b-networking-smes-startups-tickets-1980273655812','https://www.eventbrite.com/e/emirates-connect-b2b-networking-smes-startups-tickets-1980273655812','2026-05-09 00:00:00','2026-05-09 00:00:00','America/Los_Angeles','Eventbrite San Diego Events',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"c48d3abf6cb401a883982333018e7f1aa93e0b27d7d985e98d92d49d2d196353\", \"content_signature\": \"00edabba55c4b2cc8e3ac0a11184915ba1b6e83c8b4d6ef7959475ce0a29affd\", \"organizer_name\": \"Tablon Community\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1172209881%2F2927087102461%2F1%2Foriginal.20251203-040511?crop=focalpoint&fit=crop&w=512&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.5&fp-y=0.5&s=a7d3e816ec2576b2db5b02c9bbe448ad'),(50,0,NULL,'Managing concerns about attorneys and deputies','Join us for the final webinar in the series, where we\'ll be focusing on managing concerns about attorneys and deputies','2026-05-05 22:35:08','Community',7,'source','7-cabbd17e3a6a747f','https://www.eventbrite.co.uk/e/managing-concerns-about-attorneys-and-deputies-tickets-1978159019879','https://www.eventbrite.co.uk/e/managing-concerns-about-attorneys-and-deputies-tickets-1978159019879','2026-05-20 00:00:00','2026-05-20 00:00:00','America/Los_Angeles','Eventbrite San Diego Events',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"dbca83b4d6a52aa7223db9e35e086e17a0b6748c5c7909dff2320184746fef32\", \"content_signature\": \"fa1e19fbfd68567419d27eadb2e71dc06dd66025fedf8e471df43305eb0b2711\", \"organizer_name\": \"Office of the Public Guardian\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1175658393%2F449251951336%2F1%2Foriginal.20260123-164345?w=512&auto=format%2Ccompress&q=75&sharp=10&rect=0%2C112%2C3590%2C1795&s=b50851e30d5695ea5fe4e2973b3cc1bc'),(51,0,NULL,'UX Design Hackathon with UX Woman','Land $100K+ UX jobs, lead design strategy, and launch impactful startups, designing for your community & rethinking the status quo','2026-05-05 22:35:08','Community',7,'source','7-64dd874af1668397','https://www.eventbrite.com/e/ux-design-hackathon-with-ux-woman-tickets-1980891134708','https://www.eventbrite.com/e/ux-design-hackathon-with-ux-woman-tickets-1980891134708','2026-05-31 00:00:00','2026-05-31 00:00:00','America/Los_Angeles','Eventbrite San Diego Events',NULL,NULL,'San Diego',NULL,NULL,'{\"tags\": [], \"fingerprint\": \"b25cbe443eec1a2649bbf0ac67b4b72c49834057a95d204c8bc14a478739dd6d\", \"content_signature\": \"6833ac6be28c9f9fd0dc337cac4a67f02b787c098ac03bfc83bc3f841e47fb4c\", \"organizer_name\": \"UX Woman\"}',0.8,'2026-05-05 22:41:00','https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F1175260397%2F2645887045081%2F1%2Foriginal.20260119-180119?crop=focalpoint&fit=crop&w=400&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.5&fp-y=0.5&s=a28998f5bfa529a833fdf3232d73cec0');
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ingest_runs`
--

DROP TABLE IF EXISTS `ingest_runs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingest_runs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `region_id` int NOT NULL,
  `source_id` int DEFAULT NULL,
  `trigger_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fetched_count` int NOT NULL,
  `inserted_count` int NOT NULL,
  `updated_count` int NOT NULL,
  `skipped_count` int NOT NULL,
  `error_count` int NOT NULL,
  `area` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `error_summary` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `started_at` datetime DEFAULT (now()),
  `completed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_ingest_runs_region_id` (`region_id`),
  KEY `ix_ingest_runs_status` (`status`),
  KEY `ix_ingest_runs_source_id` (`source_id`),
  CONSTRAINT `ingest_runs_ibfk_1` FOREIGN KEY (`region_id`) REFERENCES `regions` (`id`),
  CONSTRAINT `ingest_runs_ibfk_2` FOREIGN KEY (`source_id`) REFERENCES `sources` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingest_runs`
--

LOCK TABLES `ingest_runs` WRITE;
/*!40000 ALTER TABLE `ingest_runs` DISABLE KEYS */;
INSERT INTO `ingest_runs` VALUES (5,0,NULL,'manual','partial_failure',2,1,0,0,2,NULL,'Gaslamp House Of Blues Events/Host Your Private Event at House of Blues San Diego! — Private Events: (asyncmy.errors.DataError) (1406, \"Data too long for column \'content\' at row 1\")\n[SQL: INSERT IN...','2026-04-28 01:17:04','2026-04-28 01:17:09'),(6,0,NULL,'manual','partial_failure',2,0,1,0,2,NULL,'Gaslamp House Of Blues Events/Host Your Private Event at House of Blues San Diego! — Private Events: (asyncmy.errors.DataError) (1406, \"Data too long for column \'content\' at row 1\")\n[SQL: INSERT IN...','2026-04-28 01:18:31','2026-04-28 01:18:38'),(8,0,NULL,'manual','success',0,0,0,1,0,NULL,NULL,'2026-04-28 01:29:24','2026-04-28 01:29:32'),(9,0,NULL,'manual','success',0,0,0,0,0,NULL,NULL,'2026-04-28 01:30:31','2026-04-28 01:30:36'),(10,0,NULL,'cli','success',48,43,5,0,0,NULL,NULL,'2026-05-05 22:24:26','2026-05-05 22:25:17'),(11,0,NULL,'cli','success',49,4,40,5,0,NULL,NULL,'2026-05-05 22:35:04','2026-05-05 22:35:43'),(12,0,NULL,'cli','success',49,0,44,5,0,NULL,NULL,'2026-05-05 22:40:55','2026-05-05 22:42:07');
/*!40000 ALTER TABLE `ingest_runs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `partner_submissions`
--

DROP TABLE IF EXISTS `partner_submissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `partner_submissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `region_id` int NOT NULL,
  `submitted_by_user_id` int DEFAULT NULL,
  `organizer_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `organizer_contact` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `instagram_handle` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `instagram_post_url` varchar(2048) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `external_event_url` varchar(2048) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `title` varchar(512) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `neighborhood` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `venue_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `venue_address` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `event_start_at` datetime DEFAULT NULL,
  `event_end_at` datetime DEFAULT NULL,
  `moderation_status` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `moderation_notes` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `published_event_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `reviewed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_partner_submissions_published_event_id` (`published_event_id`),
  KEY `ix_partner_submissions_region_id` (`region_id`),
  KEY `ix_partner_submissions_moderation_status` (`moderation_status`),
  KEY `ix_partner_submissions_submitted_by_user_id` (`submitted_by_user_id`),
  CONSTRAINT `partner_submissions_ibfk_1` FOREIGN KEY (`region_id`) REFERENCES `regions` (`id`),
  CONSTRAINT `partner_submissions_ibfk_2` FOREIGN KEY (`submitted_by_user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `partner_submissions_ibfk_3` FOREIGN KEY (`published_event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `partner_submissions`
--

LOCK TABLES `partner_submissions` WRITE;
/*!40000 ALTER TABLE `partner_submissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `partner_submissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `regions`
--

DROP TABLE IF EXISTS `regions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `regions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_regions_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `regions`
--

LOCK TABLES `regions` WRITE;
/*!40000 ALTER TABLE `regions` DISABLE KEYS */;
INSERT INTO `regions` VALUES (0,'San Diego');
/*!40000 ALTER TABLE `regions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schema_migrations`
--

DROP TABLE IF EXISTS `schema_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schema_migrations` (
  `id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schema_migrations`
--

LOCK TABLES `schema_migrations` WRITE;
/*!40000 ALTER TABLE `schema_migrations` DISABLE KEYS */;
INSERT INTO `schema_migrations` VALUES ('20260420_001_ingestion_schema.sql','2026-04-21 22:11:00');
/*!40000 ALTER TABLE `schema_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sources`
--

DROP TABLE IF EXISTS `sources`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sources` (
  `id` int NOT NULL AUTO_INCREMENT,
  `region_id` int NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `domain` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `base_url` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `category_hint` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `neighborhood` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `crawl_allowed` tinyint(1) NOT NULL,
  `crawl_delay_seconds` int NOT NULL,
  `rate_limit_per_min` int NOT NULL,
  `attribution_text` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `robots_txt_url` varchar(2048) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `terms_url` varchar(2048) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `parse_strategy` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_source_name_region` (`name`,`region_id`),
  KEY `ix_sources_is_active` (`is_active`),
  KEY `ix_sources_region_id` (`region_id`),
  KEY `ix_sources_source_type` (`source_type`),
  KEY `ix_sources_domain` (`domain`),
  KEY `ix_sources_neighborhood` (`neighborhood`),
  CONSTRAINT `sources_ibfk_1` FOREIGN KEY (`region_id`) REFERENCES `regions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sources`
--

LOCK TABLES `sources` WRITE;
/*!40000 ALTER TABLE `sources` DISABLE KEYS */;
INSERT INTO `sources` VALUES (1,0,'North Park Observatory Calendar','observatorysd.com','https://www.observatorysd.com/events/','html','Nightlife','North Park',1,1,12,5,'Source listing courtesy of official venue calendar.',NULL,NULL,'generic_html','2026-04-21 15:11:19','2026-04-21 15:11:19'),(2,0,'Gaslamp House Of Blues Events','houseofblues.com','https://www.houseofblues.com/sandiego/events','html','Nightlife','Gaslamp',1,1,12,5,'Source listing courtesy of official venue calendar.',NULL,NULL,'generic_html','2026-04-21 15:11:19','2026-04-21 15:11:19'),(3,0,'Pacific Beach Nightlife Events','pbshoreclub.com','https://www.pbshoreclub.com/events','html','Nightlife','Pacific Beach',1,1,12,5,'Source listing courtesy of official venue calendar.',NULL,NULL,'generic_html','2026-04-21 15:11:19','2026-04-21 15:11:19'),(4,0,'Hillcrest Public Events','hillcrestbia.org','https://hillcrestbia.org/events/','html','Community','Hillcrest',1,1,15,4,'Source listing courtesy of official venue calendar.',NULL,NULL,'generic_html','2026-04-21 15:11:19','2026-04-21 15:11:19'),(5,0,'Soda Bar Shows','sodabarmusic.com','https://www.sodabarmusic.com/events','html','Music','North Park',1,1,12,5,'Source listing courtesy of official venue calendar.',NULL,NULL,'generic_html','2026-04-21 15:11:19','2026-04-21 15:11:19'),(6,0,'Music Box San Diego','musicboxsd.com','https://musicboxsd.com/events/','html','Music','Little Italy',1,1,12,5,'Source listing courtesy of official venue calendar.',NULL,NULL,'generic_html','2026-04-21 15:11:19','2026-04-21 15:11:19'),(7,0,'Eventbrite San Diego Events','eventbrite.com','https://www.eventbrite.com/d/ca--san-diego/events/','html','Community',NULL,1,1,15,4,'Source listing courtesy of official venue calendar.',NULL,NULL,'generic_html','2026-05-05 15:24:25','2026-05-05 15:24:25'),(8,0,'City of San Diego Calendar','sandiego.gov','https://www.sandiego.gov/events/calendar','html','Community',NULL,1,1,15,4,'Source listing courtesy of official venue calendar.',NULL,NULL,'generic_html','2026-05-05 15:24:25','2026-05-05 15:24:25'),(9,0,'San Diego Tourism Festivals','sandiego.org','https://www.sandiego.org/events-festivals','html','Arts & Culture',NULL,1,1,15,4,'Source listing courtesy of official venue calendar.',NULL,NULL,'generic_html','2026-05-05 15:24:25','2026-05-05 15:24:25'),(10,0,'Mission Beach Boardwalk Events','mbhsd.com','https://www.mbhsd.com/events','html','Community','Mission Beach',1,1,15,4,'Source listing courtesy of official venue calendar.',NULL,NULL,'generic_html','2026-05-05 15:24:25','2026-05-05 15:24:25'),(11,0,'Whistle Stop Events','whistlestopbar.com','https://whistlestopbar.com/','html','Music','South Park',1,1,12,5,'Source listing courtesy of official venue calendar.',NULL,NULL,'generic_html','2026-05-05 15:24:25','2026-05-05 15:24:25'),(12,0,'San Diego Magazine Community Events','sandiegomagazine.com','https://sandiegomagazine.com/community-events/','html','Community',NULL,1,1,15,4,'Source listing courtesy of official venue calendar.',NULL,NULL,'generic_html','2026-05-05 15:24:25','2026-05-05 15:24:25');
/*!40000 ALTER TABLE `sources` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trends`
--

DROP TABLE IF EXISTS `trends`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trends` (
  `id` int NOT NULL AUTO_INCREMENT,
  `region_id` int NOT NULL,
  `event_id` int NOT NULL,
  `rank` int NOT NULL,
  `attendance_count` int NOT NULL,
  `comments_count` int NOT NULL,
  `likes_count` int NOT NULL,
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_trend_region_event` (`region_id`,`event_id`),
  KEY `ix_trends_event_id` (`event_id`),
  KEY `ix_trends_region_id` (`region_id`),
  CONSTRAINT `trends_ibfk_1` FOREIGN KEY (`region_id`) REFERENCES `regions` (`id`),
  CONSTRAINT `trends_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=140 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trends`
--

LOCK TABLES `trends` WRITE;
/*!40000 ALTER TABLE `trends` DISABLE KEYS */;
INSERT INTO `trends` VALUES (93,0,5,1,0,0,0,'2026-05-05 22:42:07'),(94,0,6,2,0,0,0,'2026-05-05 22:42:07'),(95,0,7,3,0,0,0,'2026-05-05 22:42:07'),(96,0,8,4,0,0,0,'2026-05-05 22:42:07'),(97,0,9,5,0,0,0,'2026-05-05 22:42:07'),(98,0,10,6,0,0,0,'2026-05-05 22:42:07'),(99,0,11,7,0,0,0,'2026-05-05 22:42:07'),(100,0,12,8,0,0,0,'2026-05-05 22:42:07'),(101,0,13,9,0,0,0,'2026-05-05 22:42:07'),(102,0,14,10,0,0,0,'2026-05-05 22:42:07'),(103,0,15,11,0,0,0,'2026-05-05 22:42:07'),(104,0,16,12,0,0,0,'2026-05-05 22:42:07'),(105,0,17,13,0,0,0,'2026-05-05 22:42:07'),(106,0,18,14,0,0,0,'2026-05-05 22:42:07'),(107,0,19,15,0,0,0,'2026-05-05 22:42:07'),(108,0,20,16,0,0,0,'2026-05-05 22:42:07'),(109,0,21,17,0,0,0,'2026-05-05 22:42:07'),(110,0,22,18,0,0,0,'2026-05-05 22:42:07'),(111,0,23,19,0,0,0,'2026-05-05 22:42:07'),(112,0,24,20,0,0,0,'2026-05-05 22:42:07'),(113,0,25,21,0,0,0,'2026-05-05 22:42:07'),(114,0,26,22,0,0,0,'2026-05-05 22:42:07'),(115,0,27,23,0,0,0,'2026-05-05 22:42:07'),(116,0,28,24,0,0,0,'2026-05-05 22:42:07'),(117,0,29,25,0,0,0,'2026-05-05 22:42:07'),(118,0,30,26,0,0,0,'2026-05-05 22:42:07'),(119,0,31,27,0,0,0,'2026-05-05 22:42:07'),(120,0,32,28,0,0,0,'2026-05-05 22:42:07'),(121,0,33,29,0,0,0,'2026-05-05 22:42:07'),(122,0,34,30,0,0,0,'2026-05-05 22:42:07'),(123,0,35,31,0,0,0,'2026-05-05 22:42:07'),(124,0,36,32,0,0,0,'2026-05-05 22:42:07'),(125,0,37,33,0,0,0,'2026-05-05 22:42:07'),(126,0,38,34,0,0,0,'2026-05-05 22:42:07'),(127,0,39,35,0,0,0,'2026-05-05 22:42:07'),(128,0,40,36,0,0,0,'2026-05-05 22:42:07'),(129,0,41,37,0,0,0,'2026-05-05 22:42:07'),(130,0,42,38,0,0,0,'2026-05-05 22:42:07'),(131,0,43,39,0,0,0,'2026-05-05 22:42:07'),(132,0,44,40,0,0,0,'2026-05-05 22:42:07'),(133,0,45,41,0,0,0,'2026-05-05 22:42:07'),(134,0,46,42,0,0,0,'2026-05-05 22:42:07'),(135,0,47,43,0,0,0,'2026-05-05 22:42:07'),(136,0,48,44,0,0,0,'2026-05-05 22:42:07'),(137,0,49,45,0,0,0,'2026-05-05 22:42:07'),(138,0,50,46,0,0,0,'2026-05-05 22:42:07'),(139,0,51,47,0,0,0,'2026-05-05 22:42:07');
/*!40000 ALTER TABLE `trends` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `region_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_users_email` (`email`),
  KEY `ix_users_region_id` (`region_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`region_id`) REFERENCES `regions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Ulises','ulisesurbina001@gmail.com','f494ba7821a0784b564b396a3e0457c053ff9dbaa9b9b1653356a764b5ad49ab','2026-04-21 02:24:52',0),(2,'test','test@gmail.com','a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3','2026-05-05 03:22:56',0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-05 19:15:31
