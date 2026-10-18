# Resumo para o Codex: projeto "Aminas vasoativas"

## Contexto

Apresentação de Bruno Dubois para uma sessão clínica de Anestesiologia e Terapia Intensiva
sobre aminas vasoativas. Orientadores: Marcelo Bandeira e Glauber Gouvea. Duração-alvo de
cerca de 18 minutos. Público: médicos (anestesiologia e UTI). Idioma: português do Brasil.

O deck foi montado no Claude (artifact "Aminas Vasoativas", tipo Slides) e depois exportado
para este repositório.

## O que o Bruno pediu, em ordem

1. Continuar o projeto de aminas vasoativas que ele fez no Claude, porque os créditos do
   projeto acabaram.
2. Usar os créditos de sessão na nuvem para isso.
3. Comparar a versão feita na sessão na nuvem com a do projeto no Claude e ficar com a melhor.
4. Entregar a apresentação em PowerPoint (.pptx).
5. Montar este resumo para o Codex.

## Estado atual

- Deck completo: 22 slides em 7 seções.
  - Abertura: capa, roteiro.
  - Fisiologia e receptores: PAM = DC × RVS, receptores, classificação (catecolaminas).
  - Drogas individuais: divisor, noradrenalina, adrenalina, dopamina, dobutamina,
    fenilefrina, efedrina, tabela-síntese.
  - Além das aminas: vasopressina, choque refratário.
  - Choque séptico: sequência SSC 2026, alvo de PAM, timing e via periférica.
  - Perioperatório: escolha da droga no intraoperatório (inclui cesárea e anafilaxia),
    alvo de PA intraoperatório.
  - Síntese: consenso e controvérsias, referências.
- Versão escolhida: a do projeto no Claude, que estava completa. A sessão na nuvem só tinha
  rascunhado 3 slides (fenilefrina, efedrina, síntese), que não foram usados.
- Correções feitas na sessão na nuvem:
  - Slide "Alvo de PAM": o OPTPRESS estava com n = 180 e mortalidade 40% vs. 30%. Corrigido
    para n = 518, mortalidade em 90 dias 39,3% vs. 28,6%, estudo interrompido por dano
    (Endo et al., Intensive Care Med 2025;51:883–892).
  - Notas do slide "Alvo intraoperatório": no HISTAP, a PAM média alcançada foi 77 mmHg no
    controle e 88 mmHg no grupo de alvo alto.
- Dados conferidos em fontes: VASSPR (JAMA 2026; 31,8% vs. 33,0%), HISTAP (n = 630; LRA
  23,5% vs. 33,7%), IMPROVE-multi (n = 1.134; 33,5% vs. 30,5%, NS), POISE-3 (13,9% vs.
  14,0%), SSC 2026 (PAM inicial 65 mmHg; vasopressina com NA em escalada; início periférico;
  corticoide condicional; sugestão contra terlipressina e levosimendan).
- PowerPoint gerado: `apresentacao/Aminas_Vasoativas.pptx`. Formato 16:9, títulos em Georgia
  e texto em Arial, tudo editável (caixas de texto e tabelas nativas), notas do apresentador
  em todos os slides, seções e transição esmaecer.

## Arquivos neste repositório

- `apresentacao/Aminas_Vasoativas.pptx`: a apresentação final.
- `apresentacao/deck/deck.json` e `apresentacao/deck/slides/*.html`: fonte do deck. Um
  arquivo por slide, cada um com um único `<section>` de 1920×1080 com estilos inline. O
  `<aside>` no fim de cada slide guarda as notas do apresentador.
- `apresentacao/conversor/html_para_pptx.js`: gera o .pptx a partir da fonte HTML.
- `RESUMO_PARA_CODEX.md`: este arquivo.

O artifact no Claude e este repositório não se sincronizam. Uma mudança feita aqui não
aparece no Claude, e vice-versa.

## Como regenerar o .pptx depois de editar um slide

```bash
cd apresentacao/conversor
npm install
npx playwright install chromium
npm run pptx
```

O conversor mede cada slide no Chromium com Georgia (via Gelasio, de mesmas métricas) e
Arial (via Liberation Sans, se instalada). Em Linux, instale `fonts-liberation` para que as
quebras de linha batam com o PowerPoint.

## Pendências

Estas dependem do Bruno:

1. Capa: preencher `[Serviço] · [Data]`.
2. Miller's Anesthesia, 10ª ed.: preencher `[cap./pág.]` nos rodapés de fisiologia,
   receptores, classificação, efedrina e intraoperatório, e `[caps.]` nas referências.

Estas são opcionais:

3. Fenilefrina: o rodapé cita uma revisão (Park & Choi, Anesth Pain Med 2024) para os dados
   de bradicardia (10,7% vs. 37,5%). Trocar pelo estudo original, Sharkey et al., Anesth
   Analg 2019;129:1312–8, depois de conferir os números no artigo.
4. Fenilefrina: o painel mostra PAM ↑ com RVS ↑↑. Avaliar se PAM ↑↑ fica mais coerente para
   um agonista α1 puro.

## Regras para continuar o trabalho

- Escrever em português do Brasil, para público médico.
- Não inventar estatística, dose, recomendação ou citação. Conferir na fonte primária e
  manter a referência no rodapé do slide.
- Manter o visual:
  - fundo claro #F5F3EE e cartões #FFFDF8;
  - azul-marinho #1B2A3A, laranja #B9581A, azul #2E5E8C, cinza #56606B;
  - títulos serifados e texto sem serifa;
  - uma ideia por slide, com a fonte no rodapé.
- Editar a fonte HTML e regenerar o .pptx, ou editar só o .pptx. Não misturar os dois sem
  sincronizar.
