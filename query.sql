create table #product 
(
product_id int primary key,
name varchar(128) not null,
rrp numeric(18,2) not null,
available_from date not null
)

create table #orders
(
order_id int primary key,
product_id int not null,
quantity int not null,
order_price numeric(18,2) not null,
dispatch_date date not null,
foreign key (product_id) references #product(product_id)
)


insert into #product values (101, 'Bayesian Method for Nonlinear Classification and Regression', 94.95, (select CONVERT(date, DATEADD(DAY, -(DATEPART(weekday, GETDATE()) + 2), GETDATE()))))
insert into #product values (102, '(next year) in Review (preorder)', 21.95, (select DATEFROMPARTS ( DATEPART(YEAR, GETDATE()) + 1, 2, 1)))
insert into #product values (103, 'Learn Python in Ten Minutes', 2.15, (select CONVERT(date, DATEADD(MONTH, -3, GETDATE()))))
insert into #product values (104, 'sports almanac (1999-2049)', 3.38, (select CONVERT(date, DATEADD(YEAR, -2, GETDATE()))))
insert into #product values (105, 'finance for dummies', 84.99, (select CONVERT(date, DATEADD(YEAR, -1, GETDATE()))))


insert into #orders values (1000, 101, 1, 90.00, (select CONVERT(date, DATEADD(MONTH, -2, GETDATE()))))
insert into #orders values (1001, 103, 1, 1.15, (select CONVERT(date, DATEADD(DAY, -40, GETDATE()))))
insert into #orders values (1002, 101, 10, 90.00, (select CONVERT(date, DATEADD(MONTH, -11, GETDATE()))))
insert into #orders values (1003, 104, 11, 3.38, (select CONVERT(date, DATEADD(MONTH, -6, GETDATE()))))
insert into #orders values (1004, 105, 11, 501.33, (select CONVERT(date, DATEADD(YEAR, -2, GETDATE()))))
insert into #orders values (1005, 102, 2, 20.78, (select CONVERT(date, DATEADD(MONTH, -13, GETDATE()))))
insert into #orders values (1006, 103, 1, 2.00, (select CONVERT(date, DATEADD(YEAR, -3, GETDATE()))))
insert into #orders values (1007, 102, 5, 21.95, (select CONVERT(date, DATEADD(DAY, -300, GETDATE()))))


select p.*, r.total_quantity from #product p
join (
	select o.product_id, SUM(o.quantity) as total_quantity from #product p 
	join #orders o on o.product_id = p.product_id 
	where DATEDIFF(YEAR, o.dispatch_date, GETDATE()) = 1
	and not ( DATEDIFF(DAY, p.available_from, GETDATE()) < 30 and DATEDIFF(DAY, p.available_from, GETDATE()) >= 0 )
	group by o.product_id
	having SUM(o.quantity) < 10
) r on r.product_id = p.product_id
order by p.product_id


