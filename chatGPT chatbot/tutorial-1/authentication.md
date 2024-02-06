{% include "./../../_shared.md" %}

# Len pre prihlásených užívateľov {#top}

Bežné tiketovacie systémy umožňujú odoslanie tiketu len prihlásenému užívateľovi.
V našom systéme je akcia kontrolera `HelpdeskTickets.submit()` verejná a nový
tiket môže vytvoriť akýkoľvek náhodný okoloidúci užívateľ, ktorý zavolá túto akciu.
Na to, aby na vytvorenie tiketu bolo potrebné prihlásiť sa, postačuje zmeniť práva
pre akcu `HelpdeskTickets.submit()` v `rights.php` modulu `Helpdesk`. Akciu odstránime
spomedzi verejných a prídáme ju každej skupine prihlásených užívateľov, ktorej
chceme povoliť vytváranie tiketov:

```php
$rights = array(
    'public' => array(
        'controlleraction' => array(
            // remove public rights
            //'HelpdeskTickets.submit' => true,
        ),
        //...
    ),
    'admins' => array(
        'controlleraction' => array(
            //...
            'HelpdeskTickets.submit' =>  $edit ? __a('Helpdesk', 'Odoslať požiadavku') : true,,
            //...
        ),
        //...
    ),
    'webmasters' => array(
        'controlleraction' => array(
            //...
            'HelpdeskTickets.submit' => true,
            //...
        ),
        //...
    ),
    'clients' => array(
        'controlleraction' => array(
            //...
            'HelpdeskTickets.submit' => true,
            //...
        ),
        //...
    ),
); 
```

Ak teraz zavoláme URL adresu `/mvc/Helpdesk/HelpdeskTickets/submit` a nie sme prihlásení, 
tak aplikácia nás najskôr presmeruje na prihlasovaciu obrazovku a po prihlásení 
nás presmeruje späť na formulár odoslania noveho tiketu. Samozrejme, ak to myslíme
s naším tiketovacím systémom vážne, tak by sme mali niekde na web stránku pridať 
link na vytvorenie nového tiketu a nespoliehať na to, že užívateľia budú spamäti
do prehliadača písať `/mvc/Helpdesk/HelpdeskTickets/submit`.

## Vlastná prihlasovacia obrazovka

...
[//]: # (Viď EshopOrders::checkout(), ::login())