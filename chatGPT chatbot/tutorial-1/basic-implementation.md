{% include "./../../_shared.md" %}

# Základná implementácia {#top}

Úvodné zadanie na vytvorenie tiketovacieho systému je nasledovné:

* Verejný (t.j. aj neprihlásený) uživateľ pomocou formuláru odošle svoju požiadavku operatorovi. Formulár bude 
obsahovať polia "Meno", "E-mail" a "Požiadavka "
* Operátorovi príde požiadavka do e-mailu a užívateľovi odpovie takisto e-mailovou správou 

Na obslúženie tejto požiadavky potrebujeme urobiť nasledovné:

* vytvoriť HTML formulár na zadanie tiketu
* napísať logiku na odolanie tiketu
* nejakým spôsobom sprístupniť vytvorenú funkcionalitu, aby ju užívateľ mohol zavolať/spustiť cez URL v prehliadači

Keďže fajnwork je založený na MVC štruktúre, tak na obslúženie horeuvedeného použijeme nasledovné:

* **view** `app/views/Tickets/form.php` použijeme na vytvorenie formuláru
* **model** `app/views/models/Ticket.php` bude mať metódu na odoslanie požiadavku
* **kontroler** `app/controllers/Tickets.php` a jeho akcia `Tickets::submit()` bude služiť ako 
pristupový bod (URL `/mvc/App/Tickets/submit`) na spustenie vytvorenej funkcionality.

Viac o MVC návrhovom vzore si prečítaj v kapitole [Teória > Všeobecne > MVC návrhový vzor][mvc-pattern]. 
Okrem uvedených MVC komponent budeme ešte potrebovať:

* nastaviť práva na prístup k novej akcii kontrolera v súbore `app/config/rights.php`
* mať niekde uloženú e-mailovú adresu na ktorú bude model tikety odosielať

Oboje bude bližšie vysvetlené nižšie v kapitolách venovaných kontroleru a modelu.
Implementáciu aplikácie začneme kontrolerom, aby sme mohli napísanu funkcionalitu 
od samého začiatku volať z prehliadača a kontrolovať priebežný stav.


## Kontroler {#controller}

Kontroler `Tickets` bude definovaný v súbore `app/controllers/Tickets.php` nasledovne 
(názov triedy je utvorený podľa názvovej konvencie, [viď Teória > Kontrolery][controllers]):


```php
<?php
class Tickets extends Controller {
    public function submit() {
        $this->displayOriginComment = true;
        return 'Hej world... je tam niekto, kto by ma nakódil?';
    }
}
```

Akcia `Tickets::submit()` bude slúžiť na odosielanie tiketov. Keď budeme chcieť odoslať
nový tiket, tak to budeme môcť urobiť na adrese `/mvc/App/Tickets/submit`. Táto 
adresa nám:

* po zavolaní zobrazí formulár nového tiketu 
* a po odoslaní tohoto formuláru tá istá akcia zariadi odoslanie našej požiadavky

Tieto dva body korešpondujú so zvyšnými dvoma položkami MVC štruktúry - view a modelom. 
Tie implementujeme nižšie a priebežne budeme tiež aktualizovať akciu kontrolera. Zatiaľ si len 
všimni že <u>akcia kontrolera nerobí `echo` ale `return` vygenerovaného obsahu (väčšinou HTML)</u> 
a že <u>v súbore s definíciou PHP triedy sa neuvádza koncový tag `?>`</u> aby sa do výstupu 
negenerovali žiadne znaky ktoré by zabránili možnosti zmeniť HTTP hlavičku (napr. kvôli 
presmerovaniu alebo nastaveniu HTTP statusu). Tiež si všimni použitie `$this->displayOriginComment = true;`
na vygenerovanie HTML komentárov, ktoré nám umožnia jednoducho idendifikovať miesto
v aplikácii kde sa daný kód generuje. Tieto kometáre sa generujú len na localhoste.

Skôr ako sa pustíme do budovania view, tak ešte musíme nastaviť práva novovytvorenej 
akcii kontrolera.

### Práva {#rights}

Naša akcia `Tickets::submit()` by mala byť verejná, t.j. prístupná ktorémukoľvek 
(aj neprihlásenému) užívateľovi. Preto v súbore `app/config/rights.php` pridáme do
zoznamu pod kľúčmi `'public' => 'controlleraction'` nasledovný riadok ([viď Teória > Práva][rights]):

```php
$rights = array(
    'public' => array(
        'controlleraction' => array(
            // ...
            'Tickets.submit' => true,
            // ...
        ),
        // ...
    ),
    // ...
);
```

Ak teraz zavoláš z prehliadača adresu `/mvc/App/Tickets/submit`, tak by sa mala zobraziť
v hlavnom obsahu tvojej webovej stránky úpenlivá prosba *"Hej world... je tam niekto, kto by ma nakódil?"*.
Je možné v tomto prípade odpovedať inak ako *"Áno!"*? Pozri sa na HTML kód cez konzolu prehliadača (vo Firefoxe je potrebné povoliť zobrazenie komentárov),
a uvidíš že vygenerované HTML obsahuje aj komentár ktorý ti pomože najsť kde v aplikácii sa
daný obsah generuje:

```html
<!--  App/controllers/Tickets.submit() -->
Hej world... je tam niekto, kto by ma nakódil?
<!--/ App/controllers/Tickets.submit() -->
```

Skús zakomentovať v `app/config/rights.php` práve pridaný riadok, otvor si `tmp/logs/rights.log`, 
znovunačítaj adresu `/mvc/App/Tickets/submit` a pozoruj čo sa deje ([viď Teória > Ladenie][debugging]).

## View {#view}

Naša view `app/views/Tickets/form.php` bude generovať HTML formulára nového tiketu nasledovným spôsobom
([viď Teória > Views][views]):

```html
<?php /* @var $this Template */
$this->displayOriginComment = true;
App::loadLib('App', 'FormHelper');
$Form = new FormHelper();
?><form method="post" class="ticket-form"><?php 
    ?><div class="title"><?php 
        echo __($this, 'New request')
    ?></div><?php
    echo $Form->hidden('_target', array(
        'explicitValue' => 'App.Tickets.submit',
    ));
    ?><br /><?php
    echo $Form->text('name', array(
        'label' => __($this, 'Name and surname'),
    ));
    ?><br /><?php
    echo $Form->email('email', array(
        'label' => __($this, 'E-mail'),
    ));
    ?><br /><?php
    echo $Form->textarea('request', array(
        'label' => __($this, 'Request'),
        'hint' => __($this, 'Please, write you request shortly and clearly'),
    ));
    ?><br /><?php
    ?><button><?php 
        echo __($this, 'Submit') 
    ?></button><?php
?></form><?php
```

Najprv cez `$this->displayOriginComment = true;` povolíme zobrazenie
komentára pôvodu vygenerovaného obsahu (generuje sa len na localhoste, všimni si
použitie poznámky na samom začiatku `/* @var $this Template */`, ktorá pomáha IDE-čku rozoznať typ `$this` v
kóde view a teda poskytovať nápovedu a dopĺňanie vlastností a metód). Potom načítame
knižnicu `FormHelper()` ([viď Teória > Všeobecne > Načítanie komponentov][loading])
a vytvoríme jej inštanciu, ktorá nám bude slúžiť na generovanie 
HTML vstupov. Následne vygenerujeme jednotivé požadované vstupy aj s popismi a 
nápovedami a na konci formulára umiestníme tlačidlo na odoslanie formulára.
[Viď Teória > Knižnice > FormHelper().][form-helper-lib]

Atribút `action` tagu `<form>` nie je uvedený, t.j. formulár sa odosiela
na tú istú URL ako je URL, ktorá ho zobrazí (t.j. na aktuálnu URL). Toto je bežná prax. V prípade potreby 
je samozrejme možné uviesť vlastnú `action` a odoslať formulár na inú adresu (viď napr. formulár tlačidla "Vložiť o košíka"  v detaile produktu).

Ako prvý vstup sa vytvorí skrytý vstup s názvom `_target ` a hodnotou `'App.Tickets.submit'`.
Tento vstup vraví aplikácii, že data daného formuláru majú byť poslané len akcii
`Tickets::submit()` v module `App` a žiadnej inej. Je dobré tento vstup nastavovať
lebo je vcelkou bežné, že na stránke je umiestnený ešte iný formulár (napr. na vyhľadávanie 
v obsahu stránky). V prípade, že data nemajú nastavený _target, tak sa pošlú všetkým
formulárom a všetky sa ich pokúsia spracovať.

Každý riadok HTML kódu je uzavretý v PHP tagoch, čo umožňuje flexibilné formátovanie a 
prelínanie PHP a HTML kódu. Výstupný HTML kód navyše neobsahuje zbytočné medzery, čo ocení aj Google.
[Viď Teória > Vývojarske nástroje > HTML nástroje.][html-tools]

### Aktualizácia akcie kontrolera {#controller-with-view}

Keďže máme pripravenú view s formulárom, bola by škoda neaktualizovať akciu kontrolera, ktorá čaká len nato:

```php
public function submit() {
    $this->displayOriginComment = true;
    return $this->loadView('Tickets/form');
}
```

Na natiahnutie view sme použili metódu `Tickets::loadView()`. Tuto metódu zdedil 
kontroler `Tickets` od svojej rodičovskej triedy `Controller`. Volanie metódy
`$this->loadView('Tickets/form')` je totožné s volaním metódy `App::loadView('App', 'Tickets/form')`.
[Viď Teória > Všeobecne > Načítanie komponentov.][loading]

A teraz šup ho `/mvc/App/Tickets/submit` do prehliadača potešiť sa:

![Formulár nového tiketu](/fajnwork/tutorial-1/img/form-1.png)

### Štýly {#styles}

To čo vidiš u seba na monitore sa môže líšiť od horeuvedeného obrázku podľa toho, na akom projekte tento tutorial skúšaš.
V každom prípade je jasné, že to potrebuje doštýlovať. Na písanie stýlov používame [LESS][less] preprocessor.
Na kompilovanie LESS do CSS používame [GULP][gulp] a tak skôr ako sa pustíš do písania štýlov, otvor si konzolu a spusti príkaz `gulp`
alebo si svoj IDE tak aby ti GULP spúšťalo same.
Viac podrobnosti o inštalácii, dostupnej funkcionalite a prepínačoch pre `gulp` nájdeš priamo v súbore `gulpfile.js` v hlavnom 
priečinku projektu. Napríklad pri ladení štýlov je celkom vhodne spustiť GULP tak, aby vygenerovaný CSS kód neminifikoval: `gulp --nonminified`.
[Viď tiež kapitolu Teória > Písanie štýlov.][css]
Nové štýly pridáme nakoniec súboru `app/css/less/main.less`:

```less
.ticket-form {
    padding: 15px 0 30px 0;
    display: table;
    margin: 0 auto;
    .title {
        font-size: 2em;
        font-weight: bold;
    }
    label {
        text-align: left;
    }
}
```

### Preklady {#translations}

Okrem štýlom potrebuje náš formulár ešte doplniť slovenské preklady. Napriek konvencii
používania slovenčiny v bežných prekladaných textoch sme v našej view použili angličtinu, 
aby bolo možné následne urobiť preklady a naučiť sa ako nato. Prekladané 
reťazce sa v kóde uvádzajú pomocou prekladovej funkcie `__()` prípadne jej názvových
verzií ([viď Teória > Preklady][translations]). Na ich extrakciu zo zdrojových kódov a preloženie používame
[Poedit][poedit]. Otvor si súbor `app/locale/App_sk_SK.po` pomocou Poedit-u a 
aktualizuj prekladané reťazce podľa aktuálneho stavu zdrojového kódu: *Catalog* > *Update from Sources*.
Doplň preklady pre novonajdené reťazce. 

Formulár tiketu by mal po pridaní štýlov a prekladov vyzerať nasledovne:

![Naštýlovaný a preložený formulár nového tiketu](/fajnwork/tutorial-1/img/form-2.png)

Formulár na odoslanie nového tiketu je hotový. Teraz sa pustíme do funkcionality
na odoslanie dat nového tiketu na helpdesk. Túto funkcionalitu implementujeme v nasledujúcej podkapitole
ako metódu modelu `Ticket`. Keď budeme mať túto funkcionalitu hotovú, tak data z formulára prepojíme
prostredníctvom kontrolera s metódou na ich odoslanie.

## Model {#model}

Biznis logika týkajúca sa požiadaviek na helpdesk bude nakódená v modeli `Ticket` definovanom
v súbore `app/models/Ticket.php` (názov triedy je utvorený podľa názvovej konvencie, [viď Teória > Modely][models]). 
Metóda `Ticket::submit()` slúži na odosielanie požiadaviek na helpdesk, t.j. na mailovú adresu helpdesku:

```php
class Ticket extends Model {
    public function submit($data) {
        $requestNumber = date('Ymdhis') . Str::getRandom(2, '0123456789');
        $subject = __($this, 'New request No. %s from %s', $requestNumber, $data['name']);
        $body = 
            __($this, 'Name') . ': ' . $data['name'] . '<br>' .
            __($this, 'Request') . ': ' . $data['request'] . '<br>';
        $to = App::getSetting('App', 'email.to');
        return App::sendEmail($body, $to, array(
            'subject' => $subject,
            'from' => $data['email'],
        ));
    }
}
```

E-mailová adresa, na ktorú sa požiadavok odošle, je pre jednoduchosť zatiaľ uvedená priamo v kóde.
Toto nie je úpne profi riešenie a nižšie to opravíme použitím nastavenia.

Požiadavok sa odošle na e-mailovú adresu aplikácie určenú na príjem e-mailových 
správ. Táto adresa je uložená v nastavení `App.email.to`. Viac o nastaveniach [viď v Teória > Nastavenia][settings].

### Aktualizácia akcie kontrolera {#controller-with-model}

Keď máme biznis logiku v modeli `Ticket` pripravenú, možeme aktualizovať akciu kontrolera:

```php
public function submit() {
    $this->displayOriginComment = true;
    if ($this->data) {
        $Ticket = $this->loadModel('Ticket', true);
        if ($Ticket->submit($this->data)) {
            App::setSuccessMessage(__($this, 'New ticket has been succesfully submited'));
            App::redirect(App::getRefererUrl('/'));
        }
        else {
            App::setErrorMessage(__($this, 'New ticket submission has failed. Try later please.'));
        }
    }
    return $this->loadView('Tickets/form');
}
```
Akcia kontrolera teraz funguje nasledovne:
* Ak nie sú prítomné žiadne formulárové data vo `$this->data` (t.j. formulár ešte
nebol odoslaný), tak sa zobrazí len prazdny formulár. Toto sa odohrá pri uvodnom
volaní URL `/mvc/App/Tickets/submit`.
* Ak formulár bol odoslaný a formulárové data `$this->data` sú prítomné, tak sa
zavolá metóda modelu `Ticket::submit()` a data sa jej odovzdajú. Ďalšie sa odvíja 
od výsledku metódy `Ticket::submit()`:
    * V prípade úspechu, keď `Ticket::submit()` vráti `true`, sa nastaví oznam o úspešnom 
odoslani tiketu a urobí sa presmerovanie akcie na seba samú aby sa zamedzilo viacnásobnému 
odoslaniu toho istého tiketu.
    * V prípade neúspechu, keď `Ticket::submit()` vráti `false`, sa nastaví chybový oznam a 
formulár tiketu sa ponecha vyplnený datami užívateľa, aby užívateľ mohol skúsiť odoslať tiket 
ešte raz neskôr.

S touto logikou zobrazenia formuláru a spracovania jeho dat sa s malými či väčšími 
obmenami stretneš ešte mnohokrát. Preto sa uisti, že jej vskutku rozumieš.

Ak teraz zavoláš URL adresu `/mvc/App/Tickets/submit`, vyplníš formulár a odošleš ho,
tak všetko by malo fungovať. Do schránky podľa nastavenia `'App.email.to'` sa odošle
správa s novým požiadavkom. Zrejme to však testuješ lokálne (na localhoste), a preto 
sa pri odosielaní e-mailov adresa doručenia prepisuje podľa aplikačnej konfigurácie `'debugEmailOptions'`
[(viď Teória > Konfiguracia)][configs]. Ak niečo nefunguje, tak začni ladiť [(vid Teória > Ladenie)][debugging].

## Slug {#slug}

URL adresa `/mvc/App/Tickets/submit` je síce funkčná, no vyzerá príliš technicky
a pre bežného užívateľa by bolo zrozumitelnejšie volať danú funkcionalitu napríklad
na URL adrese `/nova-poziadavka`. Vo fajnworku sa substitúcia dlhej mvc URL adresy 
za krátku slugovú URL adresu robí cez vytvorenie stránky s požadovaným slugom a 
následné vloženie snipetu do vytvorenej stránky ([viď Teória > Snipety a zmena MVC adries na slugy][routing-and-snippets]). 
V našom prípade by sme vytvorili stránku so slugom `nova-poziadavka` a vložili do nej snipet:

```html
<object _snippet="App.Tickets.submit" _snippet_generic="1" _snippet_name="Nova poziadavka"></object>
```

Omnoho lepším spôsobom je však použitie súboru `app/config/contents.php`. V tomto
súbore definujeme stránky, ktoré aplikácia používa. Na to, aby tieto stránky boli
skutočne k dispozícii je potrebné ich natiahnúť do databázy pomocou nástroja na 
aktualizáciu obsahov (*Admin* > *Nástroje* > *Aktualizuj obsahy webu*, 
[viď Teória > Vývojárske prostredie a nástroje > Nástroje fajnworku][fajnwork-tools]).
Nášu novú stránku definujeme v súbore `app/config/contents.php` nasledovne:

```php
$contents = array(
    //...
    'App.Tickets.submit' => array(
        'parent' => 'system',
        'name' => 'Nová požiadavka', 
        'locator' => 'nova-poziadavka', 
        'text' => '<object _snippet="App.Tickets.submit" _snippet_generic="1" _snippet_name="Nova poziadavka"></object>',
        'permanent' => 1,
    ),  
    //...
);
```

Čisto len kvôli poriadku som novú stránku zaradil medzi systémové obsahy, t.j. také
ktoré naša aplikácia bezpodmienečne potrebuje aby mohla fungovať. Tiež som jej nastavil
príznak `'permanent'` na `1`, aby ju nikto nemohol zmazať. Permanentné id obsahu (`pid`)
obsiahnuté v asociatívnom kľuči, je nastavené na `'App.Tickets.submit'` podľa akcie 
kontrolera, ktorá je danou stránkou spúšťaná. Na základe `pid`-u môžeme ziskať URL adresu 
tejto stránky v PHP kóde pomocou metódy `App::getContentUrlByPid('App.Tickets.submit')`.  
Keď máme definíciu novej stránky pripravenú, spustíme nástroj na aktualizáciu obsahov
s URL adresou: `/mvc/App/Tools/updateContents?data[module]=App`. Nové tikety teraz môžeš 
vytvárať na URL adrese `/nova-poziadavka`.