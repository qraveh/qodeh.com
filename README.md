# qodeh.com

Personal site of [Raveh Neeman](https://www.linkedin.com/in/ravehneeman/),
quantum computing researcher.

Live at <https://qodeh.com>.

## Stack

- [Hugo](https://gohugo.io/) — static site generator (**Extended edition, 0.160.1**;
  any Extended release from 0.146+ should work — the build uses Goldmark with
  `unsafe: true`, image processing, and the modern `build:` front-matter key)
- [PaperMod](https://github.com/adityatelange/hugo-PaperMod) — theme,
  vendored at `themes/PaperMod/` under its own MIT license
- GitHub Pages — hosting

## Build locally

Requires Hugo Extended ≥ 0.146 (`hugo version` should print `+extended`).

```powershell
git clone https://github.com/qraveh/qodeh.com.git
cd qodeh.com

# Run dev server (auto-reload)
hugo server
```

Open <http://localhost:1313/>.

## Contact

[raveh@qodeh.com](mailto:raveh@qodeh.com)
