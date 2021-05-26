CREATE TABLE utilizador (
	userid	 SERIAL,
	username	 VARCHAR(32) UNIQUE NOT NULL,
	email	 VARCHAR(64) UNIQUE NOT NULL,
	password	 VARCHAR(32) NOT NULL,
	adminbaniu BIGINT,
	authtoken	 VARCHAR(4096),
	PRIMARY KEY(userid)
);

CREATE TABLE administrador (
	utilizador_userid BIGINT,
	PRIMARY KEY(utilizador_userid)
);

CREATE TABLE leilao (
	leilaoid			 SERIAL,
	precominimo		 INTEGER NOT NULL,
	titulo			 VARCHAR(64) NOT NULL,
	descricao			 VARCHAR(512) NOT NULL,
	datafim			 TIMESTAMP NOT NULL,
	maiorlicitacao		 INTEGER NOT NULL,
	admincancelou		 BIGINT,
	artigoid			 VARCHAR(10) NOT NULL,
	nomeartigo		 VARCHAR(64) NOT NULL,
	descricaoartigo		 VARCHAR(512) NOT NULL,
	vendedor_utilizador_userid BIGINT NOT NULL,
	PRIMARY KEY(leilaoid)
);

CREATE TABLE licitacao (
	id				 SERIAL,
	valor			 INTEGER NOT NULL,
	valida			 BOOL NOT NULL DEFAULT true,
	momento			 TIMESTAMP NOT NULL,
	comprador_utilizador_userid BIGINT NOT NULL,
	leilao_leilaoid		 BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE mensagem (
	id		 SERIAL,
	comentario	 VARCHAR(512) NOT NULL,
	momento		 TIMESTAMP NOT NULL,
	utilizador_userid BIGINT NOT NULL,
	leilao_leilaoid	 BIGINT NOT NULL,
	PRIMARY KEY(id)
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
	descricao	 VARCHAR(512),
	leilao_leilaoid BIGINT,
	PRIMARY KEY(leilao_leilaoid)
);

CREATE TABLE notificacao (
	id		 SERIAL,
	comentario	 VARCHAR(512) NOT NULL,
	momento		 TIMESTAMP NOT NULL,
	utilizador_userid BIGINT NOT NULL,
	PRIMARY KEY(id)
);

ALTER TABLE administrador ADD CONSTRAINT administrador_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk1 FOREIGN KEY (vendedor_utilizador_userid) REFERENCES vendedor(utilizador_userid);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk1 FOREIGN KEY (comprador_utilizador_userid) REFERENCES comprador(utilizador_userid);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk2 FOREIGN KEY (leilao_leilaoid) REFERENCES leilao(leilaoid);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk2 FOREIGN KEY (leilao_leilaoid) REFERENCES leilao(leilaoid);
ALTER TABLE vendedor ADD CONSTRAINT vendedor_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE comprador ADD CONSTRAINT comprador_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE versao ADD CONSTRAINT versao_fk1 FOREIGN KEY (leilao_leilaoid) REFERENCES leilao(leilaoid);
ALTER TABLE notificacao ADD CONSTRAINT notificacao_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
