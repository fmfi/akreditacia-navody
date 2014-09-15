# Návody a impakt faktory k akreditácii

## Inštalácia

Nainštalujeme aplikáciu tak, aby bežala pod používateľom `ka`, pod Ubuntu 14.04:

```bash
# Ak ešte nemáme takého používateľa, vytvorme ho
sudo adduser --system --group -ka

# Vyvorme adresár pre aplikáciu a nahrajme zdrojové kódy
sudo mkdir -p /var/www-apps/akreditacia-navody
sudo chown ka:ka /var/www-apps/akreditacia-navody
cd /var/www-apps/akreditacia-navody
# Všimnime si bodku na konci nasledovného príkazu
sudo -u ka -H git clone https://github.com/fmfi/akreditacia-navody.git .

# Nainštalujme systémové závislosti
sudo apt-get install build-essential python-dev libpq-dev python-virtualenv
```

Prepnime sa do shellu používateľa ka:

```bash
sudo -u ka -H -s
```

Vyrobme virtualenv a nainštalujme závislosti:
 
```bash
cd /var/www-apps/akreditacia-navody
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Impakt faktory

SNIP a impakt faktory časopisov sa importujú z CSV súborov, ktoré boli medzi dokumentami akreditácie.
Schéma PostgreSQL databázy je v `if-schema.sql` a importovací skript je v `if-import.py` a `snip-import.py`,
samozrejme ich bude treba upraviť ak chceme importovať iné roky.

```bash
sudo -u ka psql akreditacia <if-schema.sql
./if-import.py 'host=localhost dbname=akreditacia user=ka password=' <if-subor.csv
./snip-import.py 'host=localhost dbname=akreditacia user=ka password=' <snip-subor.csv
```

## Konfigurácia Apache2

```ApacheConf
WSGIScriptAlias /ka/navody /var/www-apps/akreditacia-navody/navody.py
Alias /ka/navody/static /var/www-apps/akreditacia-navody/static
WSGIDaemonProcess kanavody user=ka group=ka processes=2 threads=15 display-name={%GROUP} python-path=/var/www-apps/akreditacia-navody:/var/www-apps/akreditacia-navody/venv/lib/python2.7/site-packages home=/var/www-apps/akreditacia-navody
<Directory /var/www-apps/akreditacia-navody/>
	WSGIProcessGroup kanavody
	WSGICallableObject app
	Require all granted
</Directory>
<Location /ka/navody/impakt-faktor/moje>
	CosignAllowPublicAccess Off
	AuthType Cosign
</Location>
```

> Poznámka: Uvedená Apache konfigurácia je pre verziu 2.4, pre Apache 2.2 je namiesto
> 
> ```ApacheConf
> Require all granted
> ```
>
> Treba napísať:
>
> ```ApacheConf
> Order deny,allow
> Allow from all
> ```