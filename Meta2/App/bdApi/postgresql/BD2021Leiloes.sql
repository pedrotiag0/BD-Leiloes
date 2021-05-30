CREATE TABLE utilizador (
	userid	 SERIAL,
	username	 VARCHAR(32) UNIQUE NOT NULL,
	email	 VARCHAR(64) UNIQUE NOT NULL,
	password	 VARCHAR(512) NOT NULL,
	adminbaniu BIGINT,
	authtoken	 VARCHAR(512),
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
	maiorlicitacao		 INTEGER NOT NULL DEFAULT 0,
	admincancelou		 BIGINT,
	artigoid			 VARCHAR(10) NOT NULL,
	nomeartigo		 VARCHAR(64) NOT NULL,
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
	versaoid	 SERIAL,
	titulo		 VARCHAR(64) NOT NULL,
	descricao	 VARCHAR(512) NOT NULL,
	leilao_leilaoid BIGINT,
	PRIMARY KEY(versaoid)
);

CREATE TABLE notificacao (
	id		 SERIAL,
	comentario	 VARCHAR(512) NOT NULL,
	momento		 TIMESTAMP NOT NULL,
	leilao_leilaoid	 BIGINT NOT NULL,
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
ALTER TABLE notificacao ADD CONSTRAINT notificacao_fk1 FOREIGN KEY (leilao_leilaoid) REFERENCES leilao(leilaoid);
ALTER TABLE notificacao ADD CONSTRAINT notificacao_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);

-- Trigger que notifica automaticamente os utilizadores cuja licitacao foi ultrapassada
CREATE OR REPLACE FUNCTION BidNotification() RETURNS trigger
LANGUAGE plpgsql
as $$
BEGIN
	-- Envia notificacoes
	INSERT INTO notificacao(comentario, momento, leilao_leilaoid, utilizador_userid)
	SELECT 'Licitacao ultrapassada pelo user '||new.comprador_utilizador_userid||', com o valor de '||new.valor, NOW() + INTERVAL '1 hours', new.leilao_leilaoid, comprador_utilizador_userid
	FROM licitacao
	WHERE comprador_utilizador_userid != new.comprador_utilizador_userid
		AND valor < new.valor
		AND leilao_leilaoid = new.leilao_leilaoid AND valida = true;
	
	-- Atualiza leilao
	UPDATE leilao SET maiorlicitacao = new.valor WHERE leilaoid = new.leilao_leilaoid;
    RETURN new;
END;
$$;

DROP TRIGGER IF EXISTS tLicitacaoUltrapassada on licitacao;
CREATE TRIGGER tLicitacaoUltrapassada
AFTER INSERT ON licitacao
FOR EACH ROW
EXECUTE PROCEDURE BidNotification();

-- Trigger que atualiza a tabela versao caso as propriedades do leilao sejam alteradas
create or replace function newVersionLeilao() returns trigger
language plpgsql
as $$
BEGIN
	insert into versao (titulo, descricao, leilao_leilaoid)
            values (old.titulo, old.descricao, old.leilaoid);
    return new;
END;
$$;

DROP TRIGGER IF EXISTS triggerVersion on leilao;
CREATE TRIGGER triggerVersion
AFTER UPDATE OF titulo, descricao ON leilao
FOR EACH ROW
EXECUTE PROCEDURE newVersionLeilao();

-- Trigger que notifica automaticamente os utilizadores que licitaram num leilao que foi banido
CREATE OR REPLACE FUNCTION canceledAuctionNotify() RETURNS trigger
LANGUAGE plpgsql
as $$
BEGIN
	-- Envia notificacoes
	INSERT INTO notificacao(comentario, momento, leilao_leilaoid, utilizador_userid)
	SELECT DISTINCT on (comprador_utilizador_userid) 'Lamentamos, mas o leilao '||old.titulo||' foi cancelado pelo admin userid:'||new.admincancelou||'. Pelo que as licitacoes terminaram e nao ha vencedor!', NOW() + INTERVAL '1 hours', old.leilaoid, comprador_utilizador_userid
	FROM licitacao
	WHERE leilao_leilaoid = old.leilaoid AND valida = true;
    RETURN new;
END;
$$;

DROP TRIGGER IF EXISTS tLeilaoCancelado on leilao;
CREATE TRIGGER tLeilaoCancelado
AFTER UPDATE OF admincancelou ON leilao
FOR EACH ROW
EXECUTE PROCEDURE canceledAuctionNotify();

-- Popular Base de Dados
insert into utilizador (username, email, password, adminbaniu, authtoken)
values  ('user1', 'user1@email2.com', '$pbkdf2-sha256$30000$Z2yNMaa0Vsr5n/Nei1EKoQ$QaWn1eEW0I4kmX81uP0zTN0PP30nxu3GYG00dyje6Yo', null, 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjEsImV4cCI6MTYyMjI5NTcyN30.3kfRFmZoJj1qb183rv6f0JAtVOQ6gBy8LV4c8SHBYmI'),
        ('user2', 'user2@email2.com', '$pbkdf2-sha256$30000$yhmDUMrZu3eOUQrh/F9L6Q$az.zL5D69gmA.pm.CapgpXbNGGQtJ3GHzuE1beENJF4', null, 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjQsImV4cCI6MTYyMjI5NTczM30.1TrVqi1cipxsPMUN042iyB20miif_I8dPWjqEslJ2-o'),
        ('user3', 'user3@email2.com', '$pbkdf2-sha256$30000$6P2fE6K0tra2FmLsPcc4Zw$IUcD8fkqKFArEUZ2DYkHoQVYeQKekFY3CcTHgmhE.zY', null, 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjIsImV4cCI6MTYyMjI5NTczMH0.jYaHT08t6YI1dTmI7hQP9xk-aVO-V5KIsGLIihg5QVc'),
		('user4', 'user4@email2.com', '$pbkdf2-sha256$30000$s9bae..dk9I6ZwzB2Pu/9w$8TLpsQQt21ACH/ujQ5sOFd2pEeZgGY.XrwrRiwkYzIQ', null, 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjUsImV4cCI6MTYyMjI5NTczNn0.GiOhyy7qKv1EyUT5p-uEjvlZN3S2KTfoZAGKjNZMU2U'),
        ('user5', 'user5@email2.com', '$pbkdf2-sha256$30000$/38PgTCmNOb833svBeA85w$aK0XSHR/5y2XHyFfZBwONkodGRMzjH1HHNlyp76d1i8', null, 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjYsImV4cCI6MTYyMjI5NTczOX0.ZV9l0ZFK_450PbAHH3NsMwlPMX8hxeQMxuNBDvZQmbE'),
        ('user6', 'user6@email2.com', '$pbkdf2-sha256$30000$JaR0TmktxVirtdb6H0PI.Q$BecJg9oIMQVjfj4DgIp94escGFdJStWJ.HhsLxPXIZ0', null, 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjcsImV4cCI6MTYyMjI5NTc0Mn0.JnONCzuqr9t3IKa2aOiL3g_JjvXsn_9SNXqIlrhBTxs'),
        ('user7', 'user7@email2.com', '$pbkdf2-sha256$30000$fS/l/H8PwRjjPOd8T6nV.g$WhQMd4W6RkjphVVTHiiXDP3MLIcqrbDmNKE4aE1d4fg', null, 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjgsImV4cCI6MTYyMjI5NTc0NX0.ZF3uOM-BPLDCepHqjLlEuMJHM8K_gqc42mrMfyKNcJ0'),
        ('user8', 'user8@email2.com', '$pbkdf2-sha256$30000$wpgzBuA8xxhjDMH4X0sJAQ$4dES14Cl62iEtK9BHWoDJLs/v1f8yL9bFZ/JJWjuOe0', null, 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjksImV4cCI6MTYyMjI5NTc0OH0.3z-3iLpz75weqSnnFftDPnHnMsqc_GFQo7yF5Hwo7tE'),
        ('user9', 'user9@email2.com', '$pbkdf2-sha256$30000$n5My5ty79/4/xxgDgLCW8g$0zo1zf00A6DYvc.E/DA.X.sFhXabanKbvvm4TW.j3dk', null, 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjEwLCJleHAiOjE2MjIyOTU3NTF9.DEZllTQ7FYF3_Zz-PYKNfMDW7_QbMVJFGY72QhVDPHI');

insert into comprador (moradarececao, utilizador_userid)
values  ('RuaNr92', 2),
        ('RuaNr94', 4),
        ('RuaNr95', 5),
        ('RuaNr96', 6);
		
insert into vendedor (moradaenvio, utilizador_userid)
values  ('RuaNr9', 9),
        ('RuaNr8', 8),
        ('RuaNr5', 5);
		
insert into administrador (utilizador_userid)
values  (1),
		(5);

insert into leilao (precominimo, titulo, descricao, datafim, maiorlicitacao, admincancelou, artigoid, nomeartigo, vendedor_utilizador_userid)
values  (100, 'NovoTituloLeilaoNovo', 'Nova DEscricaoNovo', '2021-06-01 20:00:00.000000', 300, null, '1234654345', 'Artigo 3', 5);

insert into licitacao (valor, valida, momento, comprador_utilizador_userid, leilao_leilaoid)
values  (115, true, '2021-05-29 12:14:26.940050', 4, 1),
        (150, true, '2021-05-29 12:16:11.079487', 4, 1),
        (250, true, '2021-05-29 12:15:40.013562', 6, 1),
        (300, true, '2021-05-29 12:14:45.874556', 2, 1);