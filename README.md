# Han Variant Reference

[English](#english) · [日本語](#日本語) · [简体中文](#简体中文) · [한국어](#한국어)

## English

A Glyphs 3 Palette plug-in for comparing regional Han glyph forms and registered ideographic variation sequences (IVS). It displays GlyphWiki SVG outlines for Japan, mainland China, Taiwan, Hong Kong, and Korea when available, plus IVS entries from the Unicode Ideographic Variation Database. Missing GlyphWiki images are hidden. Selecting a suffixed glyph, such as `.uv017`, still shows references for its unsuffixed base glyph.

The grid changes its column count with the Palette width. The slider at the bottom changes image size from 40 to 156 points and remembers the chosen size across Glyphs restarts. Double-click an IVS image to insert the matching glyph after the active glyph in the current Edit tab. For example, VS17 for `uni76F4` looks for `uni76F4.uv017`. If the glyph does not exist, the plug-in creates an empty glyph with that name in the font.

**Install:** Download or clone this repository. Put `HanVariantReference.glyphsPalette` in `~/Library/Application Support/Glyphs 3/Plugins/`, or place a symbolic link to it there. Restart Glyphs 3 and open the Palette.

**Data and limits:** The bundled IVD file is the [2026-08-03 Unicode release](https://www.unicode.org/ivd/data/2026-08-03/IVD_Sequences.txt). SVGs are fetched from [GlyphWiki](https://glyphwiki.org/) and cached in `~/Library/Caches/HanVariantReference`. GlyphWiki drawings are references, not official IRG source glyphs. Internet access is required for uncached images. The UI follows Glyphs' language setting and includes English, Japanese, Simplified and Traditional Chinese, and Korean. See [Third-party notices](THIRD_PARTY_NOTICES.md).

## 日本語

Glyphs 3 の Palette で、漢字の地域別字形と登録済み IVS を比較するプラグインです。GlyphWiki に画像がある場合、日本・中国大陸・台湾・香港・韓国の SVG 字形を表示します。IVS の一覧には Unicode の IVD を使用し、GlyphWiki に画像がない項目は表示しません。`.uv017` などのサフィックス付きグリフを選んでも、サフィックスなしの元の漢字の参考字形を表示します。

パレットの幅に合わせて列数が変わり、下部のスライダーで字形の大きさを40〜156ポイントに変更できます。設定は Glyphs の再起動後も保持されます。IVS の画像をダブルクリックすると、現在の編集タブで選択中のグリフの直後に、対応するグリフを追加します。たとえば `uni76F4` の VS17 なら `uni76F4.uv017` を探します。グリフが存在しない場合は、その名前の空グリフをフォントに作成します。

**インストール:** このリポジトリをダウンロードまたはクローンし、`HanVariantReference.glyphsPalette` を `~/Library/Application Support/Glyphs 3/Plugins/` に置くか、そこからシンボリックリンクを張ってください。Glyphs 3 を再起動して Palette を開きます。

**データと制限:** 同梱の IVD は [Unicode 2026-08-03 版](https://www.unicode.org/ivd/data/2026-08-03/IVD_Sequences.txt)です。画像は [GlyphWiki](https://glyphwiki.org/) から取得し、`~/Library/Caches/HanVariantReference` に保存します。GlyphWiki の字形は参照用であり、IRG の公式原字形ではありません。未取得の画像にはインターネット接続が必要です。UI は Glyphs の言語設定に従います。[第三者の権利表示](THIRD_PARTY_NOTICES.md)も参照してください。

## 简体中文

这是一个 Glyphs 3 调色板插件，用于比较汉字的地区字形和已登记的表意文字异体字序列（IVS）。如果 GlyphWiki 提供图像，插件会显示日本、中国大陆、台湾、香港和韩国的 SVG 字形；IVS 列表来自 Unicode 表意文字异体字数据库。没有 GlyphWiki 图像的项目不会显示。选择带有 `.uv017` 等后缀的字形时，仍显示无后缀基本字形的参考图像。

网格列数随调色板宽度变化，底部滑块可将字形大小调整为 40–156 点，设置在重启 Glyphs 后仍会保留。双击 IVS 图像，会在当前编辑标签的活动字形后插入对应的字形。例如，`uni76F4` 的 VS17 对应 `uni76F4.uv017`。如果字体中没有该字形，插件会创建一个同名的空字形。

**安装：** 下载或克隆本仓库，将 `HanVariantReference.glyphsPalette` 放入 `~/Library/Application Support/Glyphs 3/Plugins/`，也可以在该目录创建指向插件的符号链接。重启 Glyphs 3，然后打开调色板。

**数据与限制：** 随附的 IVD 文件来自 [Unicode 2026-08-03 版本](https://www.unicode.org/ivd/data/2026-08-03/IVD_Sequences.txt)。SVG 来自 [GlyphWiki](https://glyphwiki.org/)，缓存于 `~/Library/Caches/HanVariantReference`。GlyphWiki 字形仅供参考，并非 IRG 官方源字形。首次获取图像需要网络连接。界面语言跟随 Glyphs 的语言设置，也支持繁体中文。参见[第三方版权说明](THIRD_PARTY_NOTICES.md)。

## 한국어

Glyphs 3 팔레트에서 한자의 지역별 자형과 등록된 표의문자 변형 시퀀스(IVS)를 비교하는 플러그인입니다. GlyphWiki에 이미지가 있으면 일본, 중국 본토, 대만, 홍콩, 한국의 SVG 자형을 보여 줍니다. IVS 목록은 Unicode 표의문자 변형 데이터베이스를 사용하며, GlyphWiki 이미지가 없는 항목은 표시하지 않습니다. `.uv017` 같은 접미사가 붙은 글리프를 선택해도 접미사가 없는 기본 글리프의 참고 자형을 표시합니다.

팔레트 너비에 따라 격자 열 수가 바뀌고, 아래쪽 슬라이더로 자형 크기를 40~156포인트로 조절할 수 있으며, Glyphs를 다시 시작해도 설정이 유지됩니다. IVS 이미지를 두 번 클릭하면 현재 편집 탭의 활성 글리프 바로 뒤에 대응하는 글리프를 삽입합니다. 예를 들어 `uni76F4`의 VS17은 `uni76F4.uv017`을 찾습니다. 해당 글리프가 없으면 같은 이름의 빈 글리프를 폰트에 만듭니다.

**설치:** 저장소를 다운로드하거나 복제한 뒤 `HanVariantReference.glyphsPalette`를 `~/Library/Application Support/Glyphs 3/Plugins/`에 넣거나 해당 위치에 심볼릭 링크를 만듭니다. Glyphs 3을 다시 시작하고 팔레트를 엽니다.

**데이터와 제한:** 포함된 IVD 파일은 [Unicode 2026-08-03 버전](https://www.unicode.org/ivd/data/2026-08-03/IVD_Sequences.txt)입니다. SVG는 [GlyphWiki](https://glyphwiki.org/)에서 받아 `~/Library/Caches/HanVariantReference`에 저장합니다. GlyphWiki 자형은 참고용이며 공식 IRG 원본 자형이 아닙니다. 캐시되지 않은 이미지를 받으려면 인터넷 연결이 필요합니다. UI는 Glyphs의 언어 설정을 따릅니다. [제3자 고지](THIRD_PARTY_NOTICES.md)를 참고하세요.
