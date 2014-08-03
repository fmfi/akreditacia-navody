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

TODO databáza
TODO import impakt faktorov
TODO apache

