CREATE TABLE impact_factors (
  id serial primary key,
  source_title VARCHAR(255),
  source_abbr VARCHAR(255),
  snip_2008 DECIMAL(7,3),
  snip_2009 DECIMAL(7,3),
  snip_2010 DECIMAL(7,3),
  snip_2011 DECIMAL(7,3),
  snip_2012 DECIMAL(7,3),
  if_2013 DECIMAL(7,3),
  country VARCHAR(255)
);

CREATE TABLE impact_factors_issn(
  impact_factors_id int references impact_factors(id),
  issn CHAR(8),
  typ char(1),
  PRIMARY KEY (impact_factors_id, issn, typ)
);