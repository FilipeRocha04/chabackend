-- =====================================================================
-- Chá da Maya 🦋 — schema MySQL (Hostinger)
-- Execute isto uma vez no banco u235343041_chadebebe (phpMyAdmin ou CLI).
-- A API (backend/app/main.py) também cria as tabelas sozinha se elas não
-- existirem, mas este script já deixa a listinha semeada.
-- =====================================================================

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS admin_users (
  id CHAR(36) NOT NULL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  username VARCHAR(60) NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  is_admin TINYINT(1) NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS categories (
  id CHAR(36) NOT NULL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  display_order INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS gift_items (
  id CHAR(36) NOT NULL PRIMARY KEY,
  category_id CHAR(36) NOT NULL,
  name VARCHAR(255) NOT NULL,
  size VARCHAR(50) NULL,
  description TEXT NULL,
  desired_quantity INT NOT NULL DEFAULT 1,
  active TINYINT(1) NOT NULL DEFAULT 1,
  display_order INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_gift_items_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS gift_commitments (
  id CHAR(36) NOT NULL PRIMARY KEY,
  gift_item_id CHAR(36) NOT NULL,
  guest_name VARCHAR(60) NULL,
  quantity INT NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_gift_commitments_item FOREIGN KEY (gift_item_id) REFERENCES gift_items(id) ON DELETE CASCADE,
  CONSTRAINT chk_quantity CHECK (quantity >= 1 AND quantity <= 99)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX gift_commitments_item_idx ON gift_commitments (gift_item_id);

-- ---------------------------------------------------------------------
-- Listinha do Chá da Maya
-- desired_quantity reflete quantas vezes o item aparecia na sua lista
-- (fraldas RN = 4, toalha com capuz = 2, o resto = 1).
-- ---------------------------------------------------------------------
SET @cat_fraldas = UUID();
SET @cat_maya = UUID();
SET @cat_mamae = UUID();

INSERT INTO categories (id, name, display_order) VALUES
  (@cat_fraldas, 'Fraldas', 1),
  (@cat_maya, 'Mimos para Maya', 2),
  (@cat_mamae, 'Mimos para mamãe Bella', 3);

INSERT INTO gift_items (id, category_id, name, size, desired_quantity, display_order) VALUES
  (UUID(), @cat_fraldas, 'Fraldas descartáveis', 'RN', 4, 1),
  (UUID(), @cat_fraldas, 'Fraldas descartáveis', 'P',  1, 2),
  (UUID(), @cat_fraldas, 'Fraldas descartáveis', 'M',  1, 3),
  (UUID(), @cat_fraldas, 'Fraldas descartáveis', 'G',  1, 4),

  (UUID(), @cat_maya, 'Lenço umedecido sem perfume',                NULL, 1, 1),
  (UUID(), @cat_maya, 'Pomada para assadura',                       NULL, 1, 2),
  (UUID(), @cat_maya, 'Sabonete líquido da cabeça aos pés, neutro', NULL, 1, 3),
  (UUID(), @cat_maya, 'Fraldinha de boca',                          NULL, 1, 4),
  (UUID(), @cat_maya, 'Fralda de ombro',                            NULL, 1, 5),
  (UUID(), @cat_maya, 'Fralda de passeio',                          NULL, 1, 6),
  (UUID(), @cat_maya, 'Toalha com capuz',                           NULL, 2, 7),
  (UUID(), @cat_maya, 'Cueiros finos',                               NULL, 1, 8),
  (UUID(), @cat_maya, 'Kit mamadeira',                               NULL, 1, 9),

  (UUID(), @cat_maya, 'Body manga curta',                            'P', 1, 10),
  (UUID(), @cat_maya, 'Body manga curta',                            'M', 1, 11),
  (UUID(), @cat_maya, 'Body manga longa fino',                       'P', 1, 12),
  (UUID(), @cat_maya, 'Body manga longa fino',                       'M', 1, 13),
  (UUID(), @cat_maya, 'Mijão sem pé / shortinho',                    'P', 1, 14),
  (UUID(), @cat_maya, 'Mijão sem pé / shortinho',                    'M', 1, 15),
  (UUID(), @cat_maya, 'Mijão com pé fino',                           'P', 1, 16),
  (UUID(), @cat_maya, 'Mijão com pé fino',                           'M', 1, 17),
  (UUID(), @cat_maya, 'Macaquinho curto de tecido leve ou algodão',  'M', 1, 18),
  (UUID(), @cat_maya, 'Macacão longo fino de algodão',               'M', 1, 19),

  (UUID(), @cat_mamae, 'Higiene pessoal pós-parto e outros', NULL, 1, 1);
