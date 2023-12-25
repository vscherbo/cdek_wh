-- shp.cdek_print_form определение

-- Drop table

-- DROP TABLE shp.cdek_print_form;

CREATE TABLE shp.cdek_print_form (
    id serial4 NOT NULL,
    date_time timestamp NULL,
    order_uuid uuid NULL,
    form_type varchar NULL,
    url varchar NULL,
    dt_insert timestamp NULL DEFAULT now(),
    CONSTRAINT cdek_print_form_pk PRIMARY KEY (id)
);

-- Table Triggers

create trigger tr_cdek_pr_ins after insert on
shp.cdek_print_form for each row execute procedure fntr_cdek_pr_ins();

-- Permissions

ALTER TABLE shp.cdek_print_form OWNER TO arc_energo;
GRANT ALL ON TABLE shp.cdek_print_form TO arc_energo;
