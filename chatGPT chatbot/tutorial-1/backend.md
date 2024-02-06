{% include "./../../_shared.md" %}

# Administrácia {#top}

Frontend nášho tiketovacieho systému je hotový.  Potrebujeme ešte vytvoriť administráciu 
(backend). Administrácia tiketov bude obsahovať zoznam požiadavkiek, z ktorého bude možné
požiadavku otvoriť a upraviť jej obsah. Bude možné takisto vytvoriť novú požiadavku,
pre prípad, že niekto kontaktuje helpdesk telefonicky. A hoci v reálnom prípade 
je to skôr nežiaduje, tak v našom cvičnom príklade pridáme aj možnosť vymazať tiket, 
aby sme si predstavili všetky základné administračné akcie. Všetky nižšie uvedené 
administračné akcie vytvoríme v kontroleri `HelpdeskSettings` v súbore `app/modules/Helpdesk/controllers/HelpdeskSettings.php`.

## Bez použitia triedy SmartController {#without-smart-controller}

Administráčné akcie implementujeme najprv bez pomoci triedy `SmartController` a potom s ňou, aby 
sme sa naučili obe verzie, vedeli ich porovnať a na základe toho porozumeli aj zmyslu
použitia triedy `SmartController`.

### Zoznam požiadaviek {#admin-index}

Ako prvú implementujeme administračnú akciu kontrolera `HelpdeskTickets::admin_index()`, 
ktorá nám zobrazí zoznam došlých požiadaviek:

```php
public function admin_index() {
    $Ticket = $this->loadModel('HelpdeskTicket', true);
    $tickets = $Ticket->find(array(
        'order' => 'id DESC',
        'paginate' => true,
    ));
    App::setSeoTitle(__a($this, 'Požiadavky'));
    return Html::smartIndex(array(
        'title' => __a($this, 'Požiadavky'),
        'records' => $tickets,
        'Paginator' => $Ticket->Paginator,
        'columns' => array(
            'id' => __a($this, 'Číslo'),
            'name' => __a($this, 'Odosielateľ'),
            'email' => __a($this, 'E-mail'),
            'created' => __a($this, 'Čas odoslania'),
        ),
        'renderFields' => array(
            'id' => function($value) {
                // get some nice ticket number
                return str_pad($value, 5, 0, STR_PAD_LEFT);
            }
        ),
        'actions' => array(
            'add' => array(
                'url' => '/mvc/Helpdesk/HelpdeskTickets/admin_add',
            ),
        ),
        'recordActions' => array(
            'edit' => array(
                'url' => '/mvc/Helpdesk/HelpdeskTickets/admin_edit',
            ),
            'delete' => array(
                'url' => '/mvc/Helpdesk/HelpdeskTickets/admin_delete',
            ),
        ),
    ));
}
```

Kód akcie je pomerne zrozumiteľný:
* načítame model
* z databázy vytiahneme tikety zoradené od najnovšieho. Zoznam tiketov je stránkovaný.
* nastavíme titulok v tabe (záložke) stránky
* na vygenerovanie samotného zoznamu použijeme metódu `Html::smartIndex()` ([viď Teória > Knižnice > Html > Html::smartIndex()][html-lib-smart-index])

Keďže ide o administračnú akciu, tak na preklady sme použili `__a()` verziu prekladovej funkcie.
Všimni si, že medzi možnosťami metódy `Html::smartIndex()` sú uvedené už aj URL adresy 
k akciam `HelpdeskTickets::admin_add()` na vytvorenie záznamu, `HelpdeskTickets::admin_edit()` 
na úpravu existujúceho záznamu a `HelpdeskTickets::admin_delete()` na zmazanie záznamu. Tieto 
akcie zatiaľ nemáme pripravené a nemáme k ním definované ani práva. Vôbec to však nevadí, pretože
metóda `Html::smartIndex()` ignoruje všetky akcie definované v možnosti `actions` a `recordActions`, 
na ktoré užívateľ nemá právo. Akonáhle spomínané akcie naprogramujeme a pridáme im práva, 
tak v zozname došlých požiadaviek sa začnú zobrazovať. Za povšimnutie tiež stojí použitie 
`'renderFields'` na vygenerovanie pekného formátu čísla požiadavky.

Následne pridáme novej akcii `HelpdeskTickets::admin_index()` práva v súbore `app/modules/Helpdesk/config/rights.php`:

```php
$edit = !empty($edit);
$rights = array(
    //...
    'admins' => array(
        'controlleraction' => array(
            //...
            'HelpdeskTickets.admin_index' => $edit ? __a('Helpdesk', 'Zobraziť zoznam požiadaviek') : true,
        ),
        //...
    ),
    'webmasters' => array(
        'controlleraction' => array(
            //...
            'HelpdeskTickets.admin_index' => true,
        ),
        //...
    ),
); 
```

Po zavolaní URL adresy `/mvc/Helpdesk/HelpdeskTickets/admin_index` vyzerá administračný 
zoznam požiadaviek nasledovne:

![Zoznam požiadaviek](/fajnwork/tutorial-1/img/admin-index-1.png)

V prípade administračných akcií nemá význam skrývať mvc adresu za slug, tak ako sme to urobili v 
prípade frontendového formulára. Administrácia je niečo, s čím verejný užívateľ webu
neprichádza do styku a preto mvc adresy sú úplne v poriadku, ba je až nežiadúce aby
sa skrývali za slugy. Podľa URL cesty v adrese sa totíž priradujú príbuzné položky 
v navigácii administrácie.

### Úprava požiadavky {#admin-edit}

Ďalej implementujeme administračnú akciu kontrolera `HelpdeskTickets::admin_edit()`, 
ktorá nám umožní upraviť požiadavku:

```php
public function admin_edit($id = null) {
    if (!$id) {
        App::setErrorMessage(__a($this, 'Chýbajúce id požiadavky'));
        App::redirect(App::getUrl(array(
            'locator' => '/_error',
            'source' => App::$requestSource,
        )));
    }
    $Ticket = $this->loadModel('HelpdeskTicket', true);
    // save submitted data
    if ($this->data) {
        if ($Ticket->save($this->data, array(
            'alternative' => array('backend')
        ))) {
            App::setSuccessMessage(__a($this, 'Požiadavka bola úspešne aktualizovaná'));
            App::redirect(App::$url);
        }
        App::setErrorMessage(__a($this, 'Opravte prosím chyby'));

    }
    // load data on initial request
    else {
        $this->data = $Ticket->findFirstBy('id', $id);
    }
    // get some nice ticket number
    $number = str_pad($id, 5, 0, STR_PAD_LEFT);
    // display form
    App::setSeoTitle(__a($this, '"%s"', $number));
    return Html::smartForm(array(
        'title' => __a($this, 'Upraviť požiadavku č. "%s"', $number),
        'data' => $this->data,
        'Model' => $Ticket,
        'columns' => 4,
        'fields' => array(
            array('field' => 'id', 'type' => 'hidden'),
            array('h1' => __a($this, 'Požiadavka')),
            array('row'),
                array(
                    'field' => 'name', 
                    'label' => __a($this, 'Meno')
                ),
                array(
                    'field' => 'email', 
                    'label' => __a($this, 'E-mail')
                ),
                array(
                    'field' => 'created', 
                    'label' => __a($this, 'Čas vytvorenia'),
                    'type' => 'display',
                    'renderValue' => function($value) {
                        return Date::format($value, 'j.n.Y G:i');
                    },
                ),
            array('/row'),
            array('row', 'columns' => 1),
                array(
                    'field' => 'request', 
                    'label' => __a($this, 'Požiadavka'),
                ),
            array('/row'),
        )
    ));
}
```

Kód akcie robí nasledovné:
* v prípade že nebolo zadané `$id` požiadavky, tak presmerujeme na chybový screen
* ak boli odoslané data tak sa ich pokúsime uložiť:
    * ak uloženie dat prebehne úspešne, tak nastavíme potvrdzujúcu správu a akciu
presmerujeme samú na seba, aby sa zamedzilo vianásobnému odoslaniu tých istých dat 
([Post/Redirect/Get][post-redirect-get], v našom prípade by nedošlo k ničomu 
kritickému, no napriek tomu je dobrá prax, pokiaľ to je možné, používať tento prístup 
vrámci bežného spracovania formulárov)
    * ak dôjde k validačnej chybe, tak nastavíme chybovú správu
* ak ešte neboli odoslané žiadne data (úvodný *GET* dopyt na zobrazenie formulára),
tak ich vytiahneme podľa daného `$id` z databázy
* data zobrazíme vo formulári vygenerovanom pomocou `Html::smartForm()` ([viď Teória > Knižnice > Html > Html::smartForm()][html-lib-smart-form])

Za povšimnutie stojí použitie anonymnej funkcie na formátovanie dátumu vytvorenia 
požiadavky v poli `'created'`.

Dátum vytvorenia sme vo formulári uviedli ako zobrazovacie pole, pretože nechceme, 
aby túto hodnotu bolo možné meniť. Samozrejme o hekovaní formnulárov už vieme svoje
([viď Tutorial: Tiketovací systém > Odstránenie bezpečnostnej diery][tutorial-1-db-data-security])
a preto sme pri ukladaní dat nastavili alternatívu `'backend'`. Na jej základe 
urobíme v modeli validáciu poľa `'created'`, tak aby ho užívateľ nemohol prepísať, 
`HelpdeskTicket::__construct()`:

```php
$this->validations = array(
    //...
    'created' => array(
        array(
            'rule' => 'emptyValue',
            'alternative' => 'backend',
        ),
    ),    
);   
```

Iným spôsobom ako tomu zamedziť, by bolo odstránenie poľa `'created'` z dat pre prípad
alternatívy `backend` v metóde `HelpdeskTicket::normalize()`.

Následne pridáme novej akcii `HelpdeskTickets::admin_edit()` práva v súbore `app/modules/Helpdesk/config/rights.php`:

```php
$edit = !empty($edit);
$rights = array(
    //...
    'admins' => array(
        'controlleraction' => array(
            //...
            'HelpdeskTickets.admin_edit' => $edit ? __a('Helpdesk', 'Upraviť požiadavku') : true,
        ),
        //...
    ),
    'webmasters' => array(
        'controlleraction' => array(
            //...
            'HelpdeskTickets.admin_edit' => true,
        ),
        //...
    ),
); 
```

V zozname došlých požiadaviek máme teraz v riadku každej požiadavky ikonu na jej 
úpravu. Keď na ňu klikneme, tak sa nám na URL adrese `/mvc/Helpdesk/HelpdeskTickets/admin_edit/{id}`
otvorí nasledovný administračný formulár:

![Úprava požiadavky](/fajnwork/tutorial-1/img/admin-edit-1.png)

### Pridanie požiadavky {#admin-add}

Pri administračných akciach na pridanie nového záznamu máme, čo sa týka počtu 
vstupov vo formulári nového záznamu, dva zaužívané prístupy:
* Použije sa ten istý formulár ako pri editácii. V takomto pripade je vhodné, aby 
ho obidve akcie `admin_add()` a `admin_edit()` zdieľali prostredníctvom spoločnej view (*DRY*).
* Použije sa zostručnený formulár obsahujúci len povinné vstupy, často len názov
položky. Zvyšné data može užívateľ zadať v editačnom formulári záznamu, na ktorý
je presmerovaný hneď po vytvorení nového zaznamu. Toto presmerovanie sa udeje aj
pri použití prvého prístupu, no užívateľ si ho viacmenej nevšimne, keďže má pred
sebou stále ten istý formulár.

V našom prípade uplatníme prvý prístup, t.j. pri vytváraní administračnej akcie 
kontrolera `HelpdeskTickets::admin_add()` použijeme ten istý formulár ako pre akciu `admin_edit()` 
a budeme ho s ňou zdieľať pomocou spoločnej view:

```php
public function admin_add() {
    $Ticket = $this->loadModel('HelpdeskTicket', true);
    // save submitted data
    if ($this->data) {
        if ($Ticket->save($this->data)) {
            App::setSuccessMessage(__a($this, 'Nová požiadavka bola úspešne vytvorená'));
            App::redirect(App::getUrl(array(
                'module' => $this->module,
                'controller' => $this->name,
                'action' => 'admin_edit',
                'args' => array($Ticket->getPropertyId()),
                'source' => App::$requestSource,
            )));
        }
        App::setErrorMessage(__a($this, 'Opravte prosím chyby'));
    }
    // display form
    App::setSeoTitle(__a($this, 'Nová požiadavka'));
    return $this->loadView('HelpdeskTickets/admin_form', array(
        'title' => __a($this, 'Nová požiadavka'),
        'data' => $this->data,
        'Model' => $Ticket,
    ));
}
```

Kód akcie robí nasledovné:
* ak boli odoslané data tak sa ich pokúsime uložiť:
    * ak uloženie dat prebehne úspešne, tak nastavíme potvrdzujúcu správu a presmerujeme
na editáciu práve vytvoreného záznamu.
    * ak dôjde k validačnej chybe, tak nastavíme chybovú správu
* počiatočné prázdne data alebo odoslané neplatné data zobrazíme vo formulári vygenerovanom 
pomocou view `'HelpdeskTickets/admin_form'`.

Formulár požiadavky sme premiestnili do view `'HelpdeskTickets/admin_form'`. Jej 
kód je nasledovný:

```html
<?php /* @var $this Template */
$this->displayOriginComment = true;
$editation = !empty($this->params['data']['id']);
echo Html::smartForm(array(
    'title' => $this->params['title'],
    'data' => $this->params['data'],
    'Model' => $this->params['Model'],
    'columns' => 4,
    'fields' => array(
        array('if' => $editation),
            array('field' => 'id', 'type' => 'hidden'),
        array('endif'),
        array('h1' => __a($this, 'Požiadavka')),
        array('row'),
            array(
                'field' => 'name', 
                'label' => __a($this, 'Meno')
            ),
            array(
                'field' => 'email', 
                'label' => __a($this, 'E-mail')
            ),
            array('if' => $editation),
                array(
                    'field' => 'created', 
                    'label' => __a($this, 'Čas vytvorenia'),
                    'type' => 'display',
                    'renderValue' => function($value) {
                        return Date::format($value, 'j.n.Y G:i');
                    },
                ),
            array('endif'),
        array('/row'),
        array('row', 'columns' => 1),
            array(
                'field' => 'request', 
                'label' => __a($this, 'Požiadavka'),
            ),
        array('/row'),
    )
));
```

V uvedenom kóde si všimni podmienkové bloky `array('if' => $editation)`, ktoré
obmezia prítomnosť datových položiek `'id'` a `'created'` len na prípad, keď je formulár
použitý na úpravu (editáciu) požiadavky. T.j. vo formulári novej požiadavky tieto
datové položky nie sú.

Hneď aj refaktorujeme akciu `admin_edit()`, tak aby na vytvorenie formulára
tiež použivala novovytvorenú view. Na konci akcie stačí len zameniť volanie metódy
`Html::smartForm()` za nasledovné volanie view `'HelpdeskTickets/admin_form'`:

```php
public function admin_edit($id = null) {
    //...
    // display form
    App::setSeoTitle(__a($this, '"%s"', $number));
    return $this->loadView('HelpdeskTickets/admin_form', array(
        'title' => __a($this, 'Upraviť požiadavku č. "%s"', $number),
        'data' => $this->data,
        'Model' => $Ticket,
    ));
}
```

Následne pridáme novej akcii `HelpdeskTickets::admin_add()` práva v súbore `app/modules/Helpdesk/config/rights.php`:

```php
$edit = !empty($edit);
$rights = array(
    //...
    'admins' => array(
        'controlleraction' => array(
            //...
            'HelpdeskTickets.admin_add' => $edit ? __a('Helpdesk', 'Pridať požiadavku') : true,
        ),
        //...
    ),
    'webmasters' => array(
        'controlleraction' => array(
            //...
            'HelpdeskTickets.admin_add' => true,
        ),
        //...
    ),
); 
```

V zozname došlých požiadaviek máme teraz v hlavičke ikonu (+) na pridanie novej požiadavky. 
Keď na ňu klikneme, tak sa nám na URL adrese `/mvc/Helpdesk/HelpdeskTickets/admin_add`
otvorí prázdny administračný formulár na pridanie novej požiadavky.

#### Vytvorenie novej položky na základe existujúcej {#admin-add-copy}

Ak vznikne požiadavka na kopírovanie záznamov, tak pokiaľ to je možné, použijeme
na tento účel akciu `admin_add()`, ktorej pridáme nepovinný vstupný argument `$copyId`. Ak je 
`$copyId` neprázdne, tak sa formulár predvyplní datami špecifikovaného záznamu. Preto 
v takom prípade musí formulár na pridanie nového záznamu obsahovať tie isté polia 
ako formulár na úpravu záznamu. Ak by sme toto hypoteticky zapracovali do akcie 
`HelpdeskTickets::admin_add()` (hoci v prípade tiketov to nedáva zmysel), tak by
vyzerala nasledovne:

```php
public function admin_add($copyId = null) {
    $Ticket = $this->loadModel('HelpdeskTicket', true);
    // save submitted data
    if ($this->data) {
        //...
    }
    elseif (!empty($copyId)) {
        $this->data = $Ticket->findFirstBy('id', $copyId);
        unset($this->data['id']);
    }
    // display form
    //...
}
```

Všimni si, že vo vytiahnutých datach kopírovaného záznamu odstránime `'id'`, aby 
sme skutočne vytvárali nový záznam a nie editovali kopírovaný záznam. Podľa okolností
môže byť potrebné odstrániť aj iné datové položky z kopírovaného záznamu, napríklad `'sort'`
pri zoradených záznamoch, alebo určité špecifické polia ako napríklad `'ean'` a katalógové 
číslo `'code'` pri produktoch.

Pokial data nového záznamu neobsahujú súborové a prekladané polia, alebo ak aj obsahujú
tak súbory a preklady neprenášaš, tak je kopírovanie takéto jednoduché. V opačnom prípade 
je vhodné zvoliť na mieru šité riešenie a s veľkou pravdepodobnosťou implementované 
v osobitnej administračnej akcii `admin_copy()`.

### Zmazanie požiadavky {#admin-delete}

Administračná akcia kontrolera `HelpdeskTickets::admin_delete()` 
(súbor `app/modules/Helpdesk/controllers/HelpdeskSettings.php`), ktorá nám umožní zmazať požiadavku:

```php
public function admin_delete($id = null) {
    if (!$id) {
        App::setErrorMessage(__a($this, 'Chýbajúce id požiadavky'));
        App::redirect(App::getRefererUrl(App::getUrl(array(
            'locator' => '/_error',
            'source' => App::$requestSource,
        ))));
    }
    $Ticket = $this->loadModel('HelpdeskTicket', true);
    // delete
    $Ticket->deleteBy('id', $id);
    App::setSuccessMessage(__a($this, 'Požiadavka bola úspešne zmazaná'));
    App::redirect(App::getRefererUrl(App::getUrl(array(
        'locator' => '/',
        'source' => App::$requestSource,
    ))));
}
```

Kód akcie robí nasledovné:
* v prípade, že nebolo zadané `$id` požiadavky, tak presmerujeme na referera alebo ak nie
je URL adresa referera dostupná (v prípade priameho volania adresy `/mvc/Helpdesk/HelpdeskTickets/admin_delete`
bez predošlého kontextu), tak presmerujeme na chybový screen
* zmažeme požiadavku, nastavíme potvrdzujúcu správu a akciu presmerujeme na referera,
prípadne ak nie je URL adresa referera dostupná, tak na úvodnú stránku webu

Následne pridáme novej akcii `HelpdeskTickets::admin_delete()` práva v súbore `app/modules/Helpdesk/config/rights.php`:

```php
$edit = !empty($edit);
$rights = array(
    //...
    'admins' => array(
        'controlleraction' => array(
            //...
            'HelpdeskTickets.admin_delete' => $edit ? __a('Helpdesk', 'Zmazať požiadavku') : true,
        ),
        //...
    ),
    'webmasters' => array(
        'controlleraction' => array(
            //...
            'HelpdeskTickets.admin_delete' => true,
        ),
        //...
    ),
); 
```

V zozname došlých požiadaviek máme teraz v riadku každej požiadavky ikonu na jej 
zmazanie. Keď na ňu klikneme, tak sa nám zobrazí najprv vyskakovacie okno  žiadajúce 
o potvrdenie akcie. Ak akciu potvrdíme tak sa zavolá URL adresa `/mvc/Helpdesk/HelpdeskTickets/admin_delete/{id}`,
ktorá sa po vykonaní presmeruje naspäť na zoznam požiadaviek.

## Použitie triedy SmartController {#with-smart-controller}

Keď na základe horeuvedeného návodu vytvoríš administrácie pre rôzné prípady v praxi, tak zistíš
že stále dookola programuješ to isté. Menia sa len názvy modelov, nadpisy v hlavičke
zoznamov a formulárov, formulárové vstupy, trochu sa menia potvrdzujúce hlášky, občas 
metódy, ktoré použiješ na vytiahnutie a uloženie dat. Takmer vôbec sa nemení logika
kontroly argumentov, spracovania dat, presmerovania a aplikačné chybové hlášky.
Na základe tohoto poznania bola vytvorená trieda `SmartController`, ktorá ti umožňuje
naprogramovať administráčné metódy tak, aby si písal len to čo je v tvojom prípade
odlišné od ostatných prípadov. Tým sa šetrí čas, kilobajty aj energia programátora. 

V najjednoduchšej verzii sa dá administrácia pomocou triedy `SmartController` vytvoriť
len tým, že:
* kontroler vytvoríme rozšírením tejto triedy
* kontroleru nastavíme názov modelu, ktorý používa na vytiahnutie a uloženie dat
* v `rights.php` definujeme práva pre tie administračné akcie, ktoré chceme mať v administrácii dostupné

Keďže v našom prípade už práva na akcie `admin_index()`, `admin_add()`, `admin_edit()` 
a `admin_delete()` máme definované na základe predošlého, tak stačí vytvoriť kontroler 
`HelpdeskTickets` ako rozšírenie triedy `SmartController`. S veľkým prekvapením 
aj toto už je splnené, pretože trieda `HelpdeskController` je rozšírením triedy 
`SmartController` len sme o tom zatiaľ nehovorili a ani to nevyužili. Takže jediné
čo potrebujeme je nastaviť názov modelu, ktorý kontroler `HelpdeskTickets` používa
na vytiahnutie a uloženie dat. Hneď ako to urobíme tak to čo sme v tejto kapitole
do kontrolera pridali, môžeme teraz zmazať (prípadne múdro zakometovať). Kontroler 
`HelpdeskTickets` bude teraz vyzerať takmer rovnako ako pred tým než sme sa pustili 
do programovania administrácie (s tým rozdielom, že práva na administračné metódy 
už máme definované):

```php
class HelpdeskTickets extends HelpdeskController {
    protected $model = 'HelpdeskTicket';
    public function submit() {
        //...
    }
}
```

Ak teraz zavoláš URL adresu `/mvc/Helpdesk/HelpdeskTickets/admin_index`, tak to bude
robiť všetko to čo predtým, len to tak ešte nevyzerá (doslovne). V nasledovných podkapitolách
zariadime, aby to tak aj vyzeralo. 

Aby nám pri nasledovnom písaní jednotlivých akcií kontrolera fungovali nápovedy v IDE, 
tak na začiatok definície triedy `HelpdeskTickets` pridáme ešte prepísanú definíciu atribútu `Model` s určením jeho 
presného typu `HelpdeskTicket` (pôvodne je tento atribút definovaný v triede `SmartController` s typom `Model`):

```php
class HelpdeskTickets extends HelpdeskController {
    protected $model = 'HelpdeskTicket';
    /**
     * Allow the model methods hinting in IDE
     * @var HelpdeskTicket
     */
    protected $Model;
    //...
}
```
 
### Zoznam požiadaviek {#admin-smart-index}

Administračnú akciu kontrolera `HelpdeskTickets::admin_index()`, ktorá bola pôvodne napísaná takto:

```php
public function admin_index() {
    $Ticket = $this->loadModel('HelpdeskTicket', true);
    $tickets = $Ticket->find(array(
        'order' => 'id DESC',
        'paginate' => true,
    ));
    App::setSeoTitle(__a($this, 'Požiadavky'));
    return Html::smartIndex(array(
        'title' => __a($this, 'Požiadavky'),
        'records' => $tickets,
        'Paginator' => $Ticket->Paginator,
        'columns' => array(
            'id' => __a($this, 'Číslo'),
            'name' => __a($this, 'Odosielateľ'),
            'email' => __a($this, 'E-mail'),
            'created' => __a($this, 'Čas odoslania'),
        ),
        'renderFields' => array(
            'id' => function($value) {
                // get some nice ticket number
                return str_pad($value, 5, 0, STR_PAD_LEFT);
            }
        ),
        'actions' => array(
            'add' => array(
                'url' => '/mvc/Helpdesk/HelpdeskTickets/admin_add',
            ),
        ),
        'recordActions' => array(
            'edit' => array(
                'url' => '/mvc/Helpdesk/HelpdeskTickets/admin_edit',
            ),
            'delete' => array(
                'url' => '/mvc/Helpdesk/HelpdeskTickets/admin_delete',
            ),
        ),
    ));
}
```

prepíšeme na nasledovnú, aby všetko nielen fungovalo ale aj vyzeralo tak ako predtým:

```php
public function admin_index() {
    $this->viewOptions['columns'] = array(
        'id' => __a($this, 'Číslo'),
        'name' => __a($this, 'Odosielateľ'),
        'email' => __a($this, 'E-mail'),
        'created' => __a($this, 'Čas odoslania'),
    );
    $this->viewOptions['renderFields'] = array(
        'id' => function($value) {
            // get some nice ticket number
            return str_pad($value, 5, 0, STR_PAD_LEFT);
        }
    );
    $this->viewOptions['title'] = __a($this, 'Požiadavky');
    $this->seoTitle = __a($this, 'Požiadavky');
    return parent::admin_index();
}
```

Kód prepísanej akcie robí nasledovné:
* nastavíme špecifické `'columns'`, `'renderFields'` a `'title'` pre view. Je potrebné vedieť, že východzou 
view pre akciu `SmartController::admin_index()` je volanie metódy `Html::smartIndex()`, 
t.j. cez atribút `SmartController::$viewOptions` nastavujeme v tomto prípade možnosti pre
metódu `Html::smartIndex()`.
* nastavíme SEO titulok. Nie je možné to urobiť priamo volaním `App::setSeoTitle()`
ako to bolo v pôvodnej verzii, pretože `parent::admin_index()` volaný na konci musí
vedieť, že sme nastavili vlastný titulok a teda už nemá nastavovať automaticky generovaný.
* zavoláme akciu `parent::admin_index()`, ktorá urobí všetko to čo je vždy rovnaké
a čo sme neurobili mi explicitne (vytiahne požiadavky, nastaví všetky zvyšné možnosti pre `Html::smartIndex()`, ...)

### Uprava požiadavky {#admin-smart-edit}

Administračnú akciu kontrolera `HelpdeskTickets::admin_edit()`, ktorá bola pôvodne napísaná takto:

```php
public function admin_edit($id = null) {
    if (!$id) {
        App::setErrorMessage(__a($this, 'Chýbajúce id požiadavky'));
        App::redirect(App::getUrl(array(
            'locator' => '/_error',
            'source' => App::$requestSource,
        )));
    }
    $Ticket = $this->loadModel('HelpdeskTicket', true);
    // save submitted data
    if ($this->data) {
        if ($Ticket->save($this->data, array(
            'alternative' => array('backend')
        ))) {
            App::setSuccessMessage(__a($this, 'Požiadavka bola úspešne aktualizovaná'));
            App::redirect(App::$url);
        }
        App::setErrorMessage(__a($this, 'Opravte prosím chyby'));
    }
    // load data on initial request
    else {
        $this->data = $Ticket->findFirstBy('id', $id);
    }
    // get some nice ticket number
    $number = str_pad($id, 5, 0, STR_PAD_LEFT);
    // display form
    App::setSeoTitle(__a($this, '"%s"', $number));
    return $this->loadView('HelpdeskTickets/admin_form', array(
        'title' => __a($this, 'Upraviť požiadavku č. "%s"', $number),
        'data' => $this->data,
        'Model' => $Ticket,
    ));
}
```

prepíšeme na nasledovnú, aby všetko nielen fungovalo ale aj vyzeralo tak ako predtým:

```php
public function admin_edit($id = null) {
    // get some nice ticket number
    $number = str_pad($id, 5, 0, STR_PAD_LEFT);
    $this->viewOptions['title'] = __a($this, 'Upraviť požiadavku č. "%s"', $number);
    $this->view = 'HelpdeskTickets/admin_form';
    $this->seoTitle = __a($this, '"%s"', $number);
    return parent::admin_edit($id);
}
```

Kód prepísanej akcie robí nasledovné:
* nastavíme špecifické `'title'` pre view a tiež samotnú view, ktorú má akcia použiť
* nastavíme SEO titulok. Nie je možné to urobiť priamo volaním `App::setSeoTitle()`
ako to bolo v pôvodnej verzii, pretože `parent::admin_edit()` volaný na konci musí
vedieť, že sme nastavili vlastný titulok a teda už nemá nastavovať automaticky generovaný.
* zavoláme akciu `parent::admin_edit()`, ktorá urobí všetko to čo je vždy rovnaké
a čo sme neurobili mi explicitne (vytiahne data požiadavky a nastaví ich ako `'data'`
pre view, nastaví `'Model'` pre view, po odoslaní formuláru uloží data a podľa výsledku
nastaví aplikačné oznamy a urobí presmerovania)

Ak chceme byť detailisti, tak predsa sa len niečo zmení a síce aplikačný oznam po 
uspešnom uložení požiadavky. Namiesto *"Požiadavka bola úspešne aktualizovaná"* sa
zobrazí univerzálne *"Záznam bol úspešne upravený"*.

Okrem samotnej akcie aktualizujeme aj jej view. Nie je to nutné kvôli tomu, aby veci 
fungovali tak ako predtým. Urobíme to preto, že metóda `parent::admin_edit()` volaná 
na konci nastavujé niektoré implicitné parametre (napr. `'title'`, `'actions'`, 
`'Model'`, `'tabsToReloadAfterSave'`, ...) pre metódu `Html::smartForm()` použitú vo view . 
V našej pôvodnej view sme však metóde `Html::smartForm()` odovzdávali parametre 
explicitne, t.j. vymenovávali a priraďovali ich, lebo sme presne vedeli ktoré sme tam 
poslali. Týmto spôsobom sa však neodovzdajú implicitné parametre, o ktorých prítomnosti 
nemusíme nič tušiť. Takže kód view zmenime tak, že namiesto explicitného odovzávania 
parametrov metóde `Html::smartForm()`, pridáme do `$this->params` položku `'fields'` 
a `$this->params` odovzdáme celé na vstup metóde `Html::smartForm()`:

```php
<?php /* @var $this Template */
$this->displayOriginComment = true;
$editation = !empty($this->params['data']['id']);
$this->params['fields'] = array(
    // array of fields definition is the same as in the first version of view
);
echo Html::smartForm($this->params);
```
V aktuálnej verzii aplikácie to na veci nič nezmení no je to blbuvzdornejšie a
pripravené s výhľadom do budúcna. Navyše by táto verzia view fungovala aj s prvou
verziou administrácie. Zmysel to samozrejme má len z ohľadom na použitie `Html::smartForm()`
vo view.

### Pridanie požiadavky {#admin-smart-add}

Administračnú akciu kontrolera `HelpdeskTickets::admin_add()`, ktorá bola pôvodne napísaná takto:

```php
public function admin_add() {
    $Ticket = $this->loadModel('HelpdeskTicket', true);
    // save submitted data
    if ($this->data) {
        if ($Ticket->save($this->data)) {
            App::setSuccessMessage(__a($this, 'Nová požiadavka bola úspešne vytvorená'));
            App::redirect(App::getUrl(array(
                'module' => $this->module,
                'controller' => $this->name,
                'action' => 'admin_edit',
                'args' => array($Ticket->getPropertyId()),
                'source' => App::$requestSource,
            )));
        }
        App::setErrorMessage(__a($this, 'Opravte prosím chyby'));
    }
    // display form
    App::setSeoTitle(__a($this, 'Nová požiadavka'));
    return $this->loadView('HelpdeskTickets/admin_form', array(
        'title' => __a($this, 'Nová požiadavka'),
        'data' => $this->data,
        'Model' => $Ticket,
    ));
}
```

prepíšeme na nasledovnú, aby všetko nielen fungovalo ale aj vyzeralo tak ako predtým:

```php
public function admin_add() {
    $this->viewOptions['title'] = __a($this, 'Nová požiadavka');
    $this->view = 'HelpdeskTickets/admin_form';
    $this->seoTitle = __a($this, 'Nová požiadavka');
    return parent::admin_add();
}
```

Kód prepísanej akcie robí nasledovné:
* nastavíme špecifické `'title'` pre view a tiež samotnú view, ktorú má akcia použiť
* nastavíme SEO titulok. Nie je možné to urobiť priamo volaním `App::setSeoTitle()` tak
ako to bolo v pôvodnej verzii, pretože `parent::admin_add()` volaný na konci musí
vedieť, že sme nastavili vlastný titulok a teda už nemá nastavovať automaticky generovaný.
* zavoláme akciu `parent::admin_add()`, ktorá urobí všetko to čo je vždy rovnaké
a čo sme neurobili mi explicitne (nastaví `'Model'` pre view, po odoslaní formuláru 
uloží novú požiadavku a podľa výsledku nastaví aplikačné oznamy a urobí presmerovania)

Ak chceme byť detailisti, tak predsa sa len niečo zmení a síce aplikačný oznam po 
uspešnom uložení požiadavky. Namiesto *"Nová požiadavka bola úspešne vytvorená"* sa
zobrazí univerzálne *"Nový záznam bol úspešne vytvorený"*.

#### Vytvorenie novej položky na základe existujúcej {#admin-smart-add-copy}

Akcia `SmartController::admin_add()` nie je priamo predpripravená na verziu s kopírovaním záznamu.
Toto sa však dá pomerne jednoducho vyriešiť tým, že to uvedieme explicitne ako špecifický kód.
Ak by sme chceli umožniť kopírovanie požiadaviek a súčasne využiť pomoc triedy `SmartController`,
tak by sme `admin_add()` doplnili nasledovne:


```php
public function admin_add($copyId = null) {
    if (
        !empty($copyId)
        && empty($this->data)
    ) {
        $this->viewOptions['data'] = $Ticket->findFirstBy('id', $copyId);
        unset($this->viewOptions['data']['id']);
    }
    $this->viewOptions['title'] = __a($this, 'Nová požiadavka');
    $this->view = 'HelpdeskTickets/admin_form';
    $this->seoTitle = __a($this, 'Nová požiadavka');
    return parent::admin_add();
}
```

Všimni si, že data kopírovaného záznamu načítame do `$this->viewOptions['data']` a nie
do `$this->data` (ako to bolo [v pôvodnej verzii kopírovacej verzi akcie][tutorial-1-backend-admin-add-copy]).
Je to tak preto, že ak by akcia `parent::admin_add()` našla `$this->data` neprázdne, tak
by usúdila, že formulár sa už odoslal a uložila by ich. Preto pri vyúživaní preddefinovaných
akcií `SmartController::admin_add()` a `SmartController::admin_edit()` musíme rozlišovať
medzi datami posialnými do view (`$this->viewOptions['data']`) a datami, ktoré prišli
z formulára (`$this->data`).

### Zmazanie požiadavky {#admin-smart-delete}

Na to, aby fungovalo zmazanie požiadavky tak ako predtým, nemusíme robiť nič. Už 
to tak funguje a malú zmenu v aplikačnom ozname rýchlo oželieme.

## Administračné rozhranie {#navigation}

Doposiaľ sme administráciu tiketov spúšťali priamym volanim URL adresy `/mvc/Helpdesk/HelpdeskTickets/admin_index`.
Tento spôsob nám slúžil na testovanie funkčnosti počas vývoja administrácie tiketov. V bežnom produkčnom
prostredí však musí byť možné spustiť administráciu tiketov cez link prítomný v administráčnom
rozhraní. Vo fajnworku sa administračné rozhranie generuje pomocou screenu `app/screens/run.php`.
Na to, aby sme pridali administráciu tiketov do existujúceho administráčného rozhrania,
postačuje pridať definíciu novej sekcie v `'primaryMenu'` možnosti metódy `Html::smartAdmin()`
v spomínanom screene `run`:

```php
<?php 
//...
echo Html::smartAdmin(array(
    //...
    'primaryMenu' => array(
        //...
        // HELPDESK
        array(
            'label' => __a($this, 'Helpdesk'),
            'tabActivator' => '/mvc/Helpdesk/HelpdeskTickets/admin_index',
            'icon' => '<i class="fa fa-life-ring"></i>',
            'submenu' => array(                
                array(
                    'label' => __a($this, 'Tikety'),
                    'url' => '/mvc/Helpdesk/HelpdeskTickets/admin_index',
                    'icon' => '<i class="fa fa-inbox"></i>',
                ),
            ),
        ),
        //...
    ),
    //...
));
```

Uvedený kód robí nasledovné:
* Vytvorí sekciu *Helpdesk* v bočnej navigácii administračného rozhrania
* Sekcia *Helpdesk* má podsekciu *Tikety*. Táto podsekcia je súčasne nastavená ako
východzia, t.j. zobrazí sa pri kliknutí na hlavnú sekciu *Helpdesk* (viď `'tabActivator'`
sekcie zhodný s `'url'` podsekcie *Tikety*).

Všimni si, že ikony sekcie a podsekcie sú definované priamo v uvedenom kóde. V snahe, 
aby čo najviac informácii týkajúcich sa modulu bolo zapúzdrených v ňom samotnom, 
je dobrým zvykom umiestniť definicie ikon pre modul a jeho podsekcie do `config.php` 
daného modulu ako konfiguráciu `'adminIcons'`. Do súboru `app/modules/Helpdesk/config/config.php` 
pridáme konfiguraciu `'adminIcons'`:

```php
$config = array(
    'adminIcons' => array(
        'Module' => '<i class="fa fa-life-ring"></i>',
        'HelpdeskTickets' => '<i class="fa fa-inbox"></i>',
        //...
    ),   
);
```

Nasledne prepíšeme definicie ikon v screene `run`. Ikonu `'<i class="fa fa-life-ring"></i>'`
nahradíme volaním `App::getAdminIcon('Helpdesk')`. Ikonu `'<i class="fa fa-inbox"></i>'`
nahradíme volaním `App::getAdminIcon('Helpdesk', 'HelpdeskTickets')`.

Sekcia *Helpdesk* je zatiaľ stručná a pokiaľ by sa nepredpokladalo, že v nej 
pribudnú ešte ďalšie podsekcie, tak podsekciu *Tikety* by bolo možné vynechať a 
administráciu tiketov spúšťať priamo kliknutím na sekciu *Helpdesk*:

```php
<?php 
//...
echo Html::smartAdmin(array(
    //...
    'primaryMenu' => array(
        //...
        // HELPDESK
        array(
            'label' => __a($this, 'Helpdesk'),
            'url' => '/mvc/Helpdesk/HelpdeskTickets/admin_index',
            'icon' => App::getAdminIcon('Helpdesk'),
        ),
        //...
    ),
    //...
));
```

V prípade, že by sekcia *Helpdesk* bola hlavná administráčná sekcia, tak by bolo vhodné,
aby administrácia tiketov bola po príchode do administráčného rozhrania otvorená 
automaticky. Toto dosiahneme pomocou možnosti `'homeTab'` metódy `Html::smartAdmin()`:

```php
<?php 
//...
echo Html::smartAdmin(array(
    //...
    'homeTab' => array(
        'url' => '/mvc/Helpdesk/HelpdeskTickets/admin_index', 
    ),
    //...
));
```

Ak naša aplikácia zahrňa len administráčnú časť (tzv. *intranet*) - čo by mohol byť 
aj prípad tiketovacieho systému - tak cez konfiguráciu `'adminOnly' => true` v
`App` module vieme vynútiť presmerovanie neadministračných URL adries na administračný screen.

Ak je administračné rozhranie na danom projekte príliš odlišné od rozhrania definovaného
v screene `run`, tak možeme vytvoriť nový screen administračného rozhrania. Nasledne je
potrebné nastaviť konfiguráciu `'adminSlug'` v `App` module na názov nového administračného
screenu. 
