#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unicodecsv
import sys
import stdnum.issn
import psycopg2
from contextlib import closing
import re
from decimal import Decimal

csv = unicodecsv.DictReader(sys.stdin, encoding='UTF-8')

def normalize_val(val):
  val = val.strip()
  if val == '':
    return None
  return val

def normalize_issn(val, typ):
  val = normalize_val(val)
  if val == None:
    return []
  issn2 = [stdnum.issn.compact(x).zfill(8) for x in re.split(r'[,;\s]+', val)]
  issn = []
  for val in issn2:
    if (val, typ) not in issn:
      issn.append((val, typ))
      try:
        stdnum.issn.validate(val)
      except:
        print 'Warning, invalid ISSN: {}'.format(val)
  return issn

years = range(2008, 2013)

with closing(psycopg2.connect(sys.argv[1])) as conn:
  with closing(conn.cursor()) as cursor:
    for line in csv:
      title = normalize_val(line['Source Title'])
      issns = []
      issns.extend(normalize_issn(line['Print-ISSN'], 'P'))
      issns.extend(normalize_issn(line['E-ISSN'], 'E'))
      country = normalize_val(line['Country'])
      snip = {}
      for year in years:
        snip[year] = normalize_val(line['{} SNIP'.format(year)])
        snip[year] = Decimal(snip[year]) if snip[year] != None else None
      if len(issns) == 0 and snip[2012] is None:
        continue
      
      vals = [title, country]
      for year in years:
        vals.append(snip[year])
      
      cursor.execute('INSERT INTO impact_factors (source_title, country, ' + ', '.join('snip_{}'.format(x) for x in years) + ') VALUES (%s, %s' + ', %s' * len(years) + ') RETURNING id', vals)
      if_id = cursor.fetchone()[0]
      
      for issn, typ in issns:
        cursor.execute('INSERT INTO impact_factors_issn (impact_factors_id, issn, typ) VALUES (%s, %s, %s)', (if_id, issn, typ))
  conn.commit()