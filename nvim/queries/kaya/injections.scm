; Language injections for Kaya.
;
; Kaya's interpolation ({{ }}) and Liquid directives ({% %}) are highlighted
; inline by highlights.scm rather than injected as a separate language, so there
; is no external-grammar injection here yet. This file exists so editors that
; expect an injections query don't error, and as the place to add e.g. markdown
; injection into doc-comment strings if we ever want it.
