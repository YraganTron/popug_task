https://lucid.app/lucidchart/b24bde93-bd23-43e7-870e-efbc16a51cf9/edit?invitationId=inv_4147cf68-1058-45e0-a790-f4a7c30f35d4

Если у нас упадет сеть, то самое страшное, что может случиться, мы не доставим инфрормацию из таск_аппа в аккаунтинг_апп, можно решить это написав какую-то синхронизацию между бд, которая бы гарантировала бы нам, что данные и в одной бд и в другой бд по таскам совпадают. Чтобы не потерять событие assign, можем записывать в бд и потом бэкграундом обрабатывать.
Если падает база, то я не знаю, что делать. Тогда все падает, но разве репликацией эта проблема не решается? Если у нас упадет один инстанс, то другие будут жить.

Основной проблемой сейчас вижу, то что я не вижу критичных мест