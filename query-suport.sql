


### Select the features for a cartd

select 	p.payment_at,
		p.card_model, 
	   	p.card_type,
	   	t.coord_x,
	   	t.coord_y,
	   	(select count(*) as tx_1d
			from payment p1
			where p1.card_number = p.card_number
			and p1.payment_at::date = p.payment_at::date
			group by p1.card_number, p1.payment_at::date),
		(select to_char(avg(p1.amount),'FM999999999.00') as avg_1d
			from payment p1
			where p1.card_number = p.card_number
			and p1.payment_at::date = p.payment_at::date
			group by p1.card_number, p1.payment_at::date),
		(select count(*) as tx_7d
			from payment p1
			where p1.card_number = p.card_number
			and p1.payment_at::date between (p.payment_at::date - interval '6 days') and p.payment_at::date
			group by p1.card_number	),
		(select to_char(avg(p1.amount),'FM999999999.00') as avg_7d
			from payment p1
			where p1.card_number = p.card_number
			and p1.payment_at::date between (p.payment_at::date - interval '6 days') and p.payment_at::date
			group by p1.card_number	),
		(select count(*) as tx_30d
			from payment p1
			where p1.card_number = p.card_number
			and p1.payment_at::date between (p.payment_at::date - interval '31 days') and p.payment_at::date
			group by p1.card_number	),
		(select to_char(avg(p1.amount),'FM999999999.00') as avg_30d
			from payment p1
			where p1.card_number = p.card_number
			and p1.payment_at::date between (p.payment_at::date - interval '31 days') and p.payment_at::date
			group by p1.card_number	),
		to_char(coalesce ( (select extract(epoch from p.payment_at - p1.payment_at )
			from payment p1 
			where p1.card_number = p.card_number
			and p1.payment_at < p.payment_at
			order by p1.payment_at desc
			limit 1),0),'FM999999999') as time_btw_cc_tx
from payment p,
	terminal t
where p.fk_terminal_id = t.id
and p.card_number = '222.111.000.002'
order by p.payment_at desc
limit 1

### Select a bunch of cards per period. This query is used to prepare the dataset

select  ROW_NUMBER() OVER (ORDER BY p.payment_at) as id,
		p.fk_card_id,	
		p.card_number,
		p.terminal_name,
		t.coord_x,
		t.coord_y, 
		p.card_type,
		p.card_model,
		p.payment_at,
		p.mcc,
		p.amount,
		CASE WHEN p.payment_at::time <  '08:00' THEN 'night'
            WHEN p.payment_at::time >= '20:00' THEN 'night'
            ELSE 'day' END AS night_day,
		CASE WHEN p.payment_at::time <  '08:00' THEN '1'
            WHEN p.payment_at::time >= '20:00' THEN '1'
            ELSE '0' END AS ic_night_day,
		CASE WHEN extract(DOW from p.payment_at) in(0,6) then 'wkend' 
		    ELSE 'wkday' end as wkend_wkday,
		CASE WHEN extract(DOW from p.payment_at) in(0,6) then '1' 
		    ELSE '0' end as ic_wkend_wkday,
		 EXTRACT('doy' FROM p.payment_at)
         AS  day_of_year,
		(select count(*) as tx_1d
			from payment p1
			where p1.card_number = p.card_number
			and p1.payment_at::date = p.payment_at::date
			group by p1.card_number, p1.payment_at::date),
		(select to_char(avg(p1.amount),'FM999999999.00') as avg_1d
			from payment p1
			where p1.card_number = p.card_number
			and p1.payment_at::date = p.payment_at::date
			group by p1.card_number, p1.payment_at::date),
		(select count(*) as tx_7d
			from payment p1
			where p1.card_number = p.card_number
			and p1.payment_at::date between (p.payment_at::date - interval '6 days') and p.payment_at::date
			group by p1.card_number	),
		(select to_char(avg(p1.amount),'FM999999999.00') as avg_7d
			from payment p1
			where p1.card_number = p.card_number
			and p1.payment_at::date between (p.payment_at::date - interval '6 days') and p.payment_at::date
			group by p1.card_number	),
		(select count(*) as tx_30d
			from payment p1
			where p1.card_number = p.card_number
			and p1.payment_at::date between (p.payment_at::date - interval '31 days') and p.payment_at::date
			group by p1.card_number	),
		(select to_char(avg(p1.amount),'FM999999999.00') as avg_30d
			from payment p1
			where p1.card_number = p.card_number
			and p1.payment_at::date between (p.payment_at::date - interval '31 days') 
			and p.payment_at::date
			group by p1.card_number	),
		to_char(coalesce ( extract(epoch from p.payment_at - (lag(p.payment_at) over (ORDER BY p.payment_at desc))),0) *-1,'FM999999999') as time_btw_tx,
		to_char(coalesce ( (select extract(epoch from p.payment_at - p1.payment_at )
			from payment p1 
			where p1.card_number = p.card_number
			and p1.payment_at < p.payment_at
			and p1.payment_at::date = p.payment_at::date
			order by p1.payment_at desc
			limit 1),0),'FM999999999') as time_btw_cc_tx,
			to_char(p.fraud,'FM999999999') as fraud
from payment p,
	terminal t
where p.fk_terminal_id = t.id
and p.payment_at::date >= '2024-04-01' 
and p.payment_at::date <= '2024-05-31'
order by p.payment_at asc

### DDL

-- public.payment definition

-- Drop table

-- DROP TABLE public.payment;

CREATE TABLE public.payment (
	id serial4 NOT NULL,
	fk_card_id int4 NULL,
	card_number varchar(200) NULL,
	fk_terminal_id int4 NULL,
	terminal_name varchar(200) NULL,
	card_type varchar(200) NULL,
	card_model varchar(200) NULL,
	payment_at timestamptz NULL,
	mcc varchar(10) NULL,
	status varchar(200) NULL,
	currency varchar(10) NULL,
	amount float8 NULL,
	create_at timestamptz NULL,
	update_at timestamptz NULL,
	tenant_id varchar(200) NULL,
	fraud float8 NULL,
	CONSTRAINT payment_pkey PRIMARY KEY (id)
);
CREATE INDEX payment_idx ON public.payment USING btree (card_number);


-- public.payment foreign keys

ALTER TABLE public.payment ADD CONSTRAINT payment_fk_card_id_fkey FOREIGN KEY (fk_card_id) REFERENCES public.card(id);
ALTER TABLE public.payment ADD CONSTRAINT payment_fk_terminal_id_fkey FOREIGN KEY (fk_terminal_id) REFERENCES public.terminal(id);

-- public.terminal definition

-- Drop table

-- DROP TABLE public.terminal;

CREATE TABLE public.terminal (
	id serial4 NOT NULL,
	terminal_name varchar(200) NULL,
	coord_x float8 NULL,
	coord_y float8 NULL,
	status varchar(200) NULL,
	create_at timestamptz NULL,
	update_at timestamptz NULL,
	CONSTRAINT terminal_pkey PRIMARY KEY (id)
);