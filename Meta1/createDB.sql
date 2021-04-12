CREATE TABLE utilizador (
	userid	 BIGINT,
	username VARCHAR(32) UNIQUE NOT NULL,
	email	 VARCHAR(64) UNIQUE NOT NULL,
	password VARCHAR(32) NOT NULL,
	banido	 BOOL NOT NULL DEFAULT false,
	PRIMARY KEY(userid)
);

CREATE TABLE administrador (
	utilizador_userid BIGINT,
	PRIMARY KEY(utilizador_userid)
);

CREATE TABLE artigo (
	artigoid			 VARCHAR(10),
	nome			 VARCHAR(32) NOT NULL,
	descricao			 VARCHAR(512),
	vendedor_utilizador_userid BIGINT NOT NULL,
	PRIMARY KEY(artigoid)
);

CREATE TABLE leilao (
	leilaoid			 BIGINT,
	precominimo		 INTEGER NOT NULL,
	titulo			 VARCHAR(32) NOT NULL,
	descricao			 VARCHAR(512) NOT NULL,
	datafim			 TIMESTAMP NOT NULL,
	cancelado			 BOOL NOT NULL DEFAULT true,
	vendedor_utilizador_userid BIGINT NOT NULL,
	artigo_artigoid		 VARCHAR(10) UNIQUE NOT NULL,
	PRIMARY KEY(leilaoid)
);

CREATE TABLE licitacao (
	valor			 INTEGER NOT NULL,
	valida			 BOOL DEFAULT true,
	comprador_utilizador_userid BIGINT NOT NULL,
	leilao_leilaoid		 BIGINT NOT NULL
);

CREATE TABLE mensagem (
	comentario	 VARCHAR(128) NOT NULL,
	momento		 TIMESTAMP NOT NULL,
	utilizador_userid BIGINT NOT NULL,
	leilao_leilaoid	 BIGINT NOT NULL
);

CREATE TABLE vendedor (
	moradaenvio	 VARCHAR(128),
	utilizador_userid BIGINT,
	PRIMARY KEY(utilizador_userid)
);

CREATE TABLE comprador (
	moradarececao	 VARCHAR(128),
	utilizador_userid BIGINT,
	PRIMARY KEY(utilizador_userid)
);

ALTER TABLE administrador ADD CONSTRAINT administrador_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE artigo ADD CONSTRAINT artigo_fk1 FOREIGN KEY (vendedor_utilizador_userid) REFERENCES vendedor(utilizador_userid);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk1 FOREIGN KEY (vendedor_utilizador_userid) REFERENCES vendedor(utilizador_userid);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk2 FOREIGN KEY (artigo_artigoid) REFERENCES artigo(artigoid);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk1 FOREIGN KEY (comprador_utilizador_userid) REFERENCES comprador(utilizador_userid);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk2 FOREIGN KEY (leilao_leilaoid) REFERENCES leilao(leilaoid);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk2 FOREIGN KEY (leilao_leilaoid) REFERENCES leilao(leilaoid);
ALTER TABLE vendedor ADD CONSTRAINT vendedor_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE comprador ADD CONSTRAINT comprador_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);

