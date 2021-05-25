CREATE TABLE utilizador (
	userid	 SERIAL,
	username	 VARCHAR(32) UNIQUE NOT NULL,
	email	 VARCHAR(64) UNIQUE NOT NULL,
	password	 VARCHAR(32) NOT NULL,
	adminbaniu BIGINT,
	PRIMARY KEY(userid)
);

CREATE TABLE administrador (
	utilizador_userid BIGINT,
	PRIMARY KEY(utilizador_userid)
);

CREATE TABLE artigo_leilao (
	artigoid			 VARCHAR(10),
	nome			 VARCHAR(32) NOT NULL,
	descricao			 VARCHAR(512) NOT NULL,
	leilao_leilaoid		 BIGINT UNIQUE NOT NULL,
	leilao_precominimo	 INTEGER NOT NULL,
	leilao_titulo		 VARCHAR(64) NOT NULL,
	leilao_descricao		 VARCHAR(512) NOT NULL,
	leilao_datafim		 TIMESTAMP NOT NULL,
	leilao_maiorlicitacao	 INTEGER NOT NULL,
	leilao_admincancelou	 BIGINT,
	vendedor_utilizador_userid BIGINT NOT NULL,
	PRIMARY KEY(artigoid)
);

CREATE TABLE licitacao (
	valor			 INTEGER NOT NULL,
	valida			 BOOL NOT NULL DEFAULT true,
	comprador_utilizador_userid BIGINT NOT NULL,
	artigo_leilao_artigoid	 VARCHAR(10) NOT NULL
);

CREATE TABLE mensagem (
	comentario		 VARCHAR(512) NOT NULL,
	momento		 TIMESTAMP NOT NULL,
	utilizador_userid	 BIGINT NOT NULL,
	artigo_leilao_artigoid VARCHAR(10) NOT NULL
);

CREATE TABLE vendedor (
	moradaenvio	 VARCHAR(128) NOT NULL,
	utilizador_userid BIGINT,
	PRIMARY KEY(utilizador_userid)
);

CREATE TABLE comprador (
	moradarececao	 VARCHAR(128) NOT NULL,
	utilizador_userid BIGINT,
	PRIMARY KEY(utilizador_userid)
);

CREATE TABLE versao (
	titulo		 VARCHAR(64) NOT NULL,
	descricao		 VARCHAR(512),
	artigo_leilao_artigoid VARCHAR(10) NOT NULL
);

CREATE TABLE notificacao (
	comentario	 VARCHAR(512) NOT NULL,
	momento		 TIMESTAMP NOT NULL,
	utilizador_userid BIGINT NOT NULL
);

ALTER TABLE administrador ADD CONSTRAINT administrador_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE artigo_leilao ADD CONSTRAINT artigo_leilao_fk1 FOREIGN KEY (vendedor_utilizador_userid) REFERENCES vendedor(utilizador_userid);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk1 FOREIGN KEY (comprador_utilizador_userid) REFERENCES comprador(utilizador_userid);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk2 FOREIGN KEY (artigo_leilao_artigoid) REFERENCES artigo_leilao(artigoid);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk2 FOREIGN KEY (artigo_leilao_artigoid) REFERENCES artigo_leilao(artigoid);
ALTER TABLE vendedor ADD CONSTRAINT vendedor_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE comprador ADD CONSTRAINT comprador_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE versao ADD CONSTRAINT versao_fk1 FOREIGN KEY (artigo_leilao_artigoid) REFERENCES artigo_leilao(artigoid);
ALTER TABLE notificacao ADD CONSTRAINT notificacao_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);

