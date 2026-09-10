# corrode Rust Consulting

We might not know each other yet, but I'm excited to meet you!
I'm [Matthias Endler](https://endler.dev), a Rust consultant and trainer.

I've been working with Rust since 2015 and I've been consulting since 2020.
My specialty is helping companies to adopt Rust and integrate it into their
existing codebase.

Check out my [consulting page](https://corrode.dev) for more details.
This is the source code of that website. 🦀

## Local development

Install [Zola 0.23.4](https://www.getzola.org/documentation/getting-started/installation/),
matching CI. Run `make dev` to start the site with drafts, or `make build` for a
production build.

Reusable template and content components live in `templates/components/`.
The site uses Tera 2 component syntax and requires Zola 0.23 or newer.

### Component conventions

- Declare required parameter types; let defaults infer optional parameter types.
- Pass dependencies explicitly: components do not inherit the caller's context.
- Use attribute shorthand when names match (`{{ <example title /> }}` instead of
  `{{ <example title={title} /> }}`). Keep expressions explicit when they differ.
- Use optional chaining for optional metadata and ternaries for simple choices.
- Preserve whitespace controls in content components: extra indentation or blank
  lines can cause their HTML to render as Markdown code blocks.

See the [Tera component reference](https://keats.github.io/tera/#components) for
self-closing calls, block bodies, and parameter syntax.

## Credits

The theme is based on [ntun](https://github.com/Netoun/ntun) by 
[Nicolas Coulonnier](https://github.com/Netoun).