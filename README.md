# Сайт Solar

Статический сайт из 9 страниц, без сборщиков. Откройте `index.html` в браузере или загрузите всю папку на любой хостинг (GitHub Pages, Netlify, Cloudflare Pages).

Страницы: `index.html`, `features.html`, `download.html`, `install-ios.html`, `changelog.html`, `about.html`, `devparty.html`, `community.html`, `terms.html`, `privacy.html`.

## Как обновлять

Страницы генерирует `tools/build.py`:

```bash
pip install markdown
python3 tools/build.py
```

- Юридические тексты: `content/TERMS.md` и `content/PRIVACY.md`. Всё в [квадратных скобках] подсвечивается на сайте как незаполненное поле.
- История версий: добавьте `content/RELEASE-NOTES-X.Y.Z.md` и поменяйте `LATEST` в начале `tools/build.py`.
- Ссылки на загрузку, Discord и Telegram: константы в начале `tools/build.py` (`TELEGRAM_URL` пока пустая).

## Анимации и 3D

- `assets/anim.js`: появление блоков при прокрутке, 3D-наклон карточек и телефонов за курсором, «магнитные» кнопки, свечение за курсором, полоса прокрутки, плавные переходы между страницами, 3D-орбита в шапках страниц.
- `assets/hero3d.js` + `assets/three.min.js` (three.js r128, лицензия MIT в `three.LICENSE.txt`): 3D-сфера из жидкого металла на главной. Клик по странице заставляет её «всплеснуть».
- Если в системе включено «Уменьшение движения», анимации отключаются.
- Название бренда задаётся константой `BRAND` в `tools/build.py`.
