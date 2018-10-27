
CREATE TABLE IF NOT EXISTS `player` (
  `uid` bigint(20) unsigned NOT NULL COMMENT '角色唯一ID',
  `account` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '玩家账号',
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色昵称',
  `authority` smallint(6) unsigned NOT NULL COMMENT '玩家权限',
  `level` smallint(6) unsigned NOT NULL COMMENT '角色等级',
  `vip_level` int(10) unsigned NOT NULL COMMENT 'VIP等级',
  `exp` int(11) unsigned NOT NULL COMMENT '经验',
  `diamond` int(11) unsigned NOT NULL COMMENT '钻石数量',
  `coin` int(10) unsigned NOT NULL COMMENT '货币',
  `strength_point` int(10) unsigned NOT NULL COMMENT '体力',
  `birth_date` datetime NOT NULL COMMENT '角色创建日期',
  `register_ip` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '注册IP',
  `ban_expire` bigint(20) NOT NULL COMMENT '封禁到期时间',
  `is_banned` tinyint(1) unsigned NOT NULL COMMENT '是否被封禁',
  `shield_expire` bigint(20) NOT NULL COMMENT '保护罩时间',
  `current_guide_chapter` int(10) unsigned NOT NULL COMMENT '当前引导章节',
  PRIMARY KEY (`uid`),
  UNIQUE KEY `Id` (`uid`),
  UNIQUE KEY `account` (`account`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色信息';