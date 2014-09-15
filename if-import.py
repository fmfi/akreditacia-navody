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
    if (val, typ) not in issn and val != '********':
      issn.append((val, typ))
      try:
        stdnum.issn.validate(val)
      except:
        print 'Warning, invalid ISSN: {}'.format(val)
  return issn

seen_issns = set()

with closing(psycopg2.connect(sys.argv[1])) as conn:
  with closing(conn.cursor()) as cursor:
    for line in csv:
      abbr = normalize_val(line['Abbreviated Journal Title(linked to journal information)'])
      issns = []
      issns.extend(normalize_issn(line['ISSN'], '?'))
      impact_factor = normalize_val(line['Impact Factor'])
      impact_factor = Decimal(impact_factor) if impact_factor is not None else None
      if len(issns) == 0 or impact_factor is None:
        continue
      
      vals = [abbr, impact_factor]
      
      cursor.execute('SELECT DISTINCT impact_factors_id FROM impact_factors_issn WHERE issn IN (' + ', '.join(['%s']*len(issns)) + ')', [x[0] for x in issns])
      
      if_ids = cursor.fetchall()
      
      if len(if_ids) == 0:
        cursor.execute('INSERT INTO impact_factors (source_abbr, if_2013) VALUES (%s, %s) RETURNING id', vals)
        if_id = cursor.fetchone()[0]
        print 'Warning, not found:', abbr, ' '.join([x[0] for x in issns])
      elif len(if_ids) == 1:
        if_id = if_ids[0][0]
        cursor.execute('UPDATE impact_factors SET source_abbr = %s, if_2013 = %s WHERE id = %s', vals + [if_id])
      for issn, typ in issns:
        if issn not in seen_issns:
          cursor.execute('INSERT INTO impact_factors_issn (impact_factors_id, issn, typ) VALUES (%s, %s, %s)', (if_id, issn, typ))
          seen_issns.add(issn)
        else:
          print 'Warning, duplicate ISSN for if_id = {}'.format(if_id)
  conn.commit()