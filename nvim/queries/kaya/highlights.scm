; Tree-sitter highlight queries for Kaya.
;
; Capture names follow the nvim-treesitter convention (@keyword, @function.call,
; @string, ...). The shared conformance suite maps these to its normalized
; categories in packages/kaya_syntax_tests/harness/capture-map.ts.
;
; Order matters: later captures override earlier ones for the same node, so put
; the most specific rules last.

; ------------------------------------------------------------------- comments
(line_comment) @comment
(block_comment) @comment

; ------------------------------------------------------------------- literals
(number) @number
(boolean) @constant.builtin
(null) @constant.builtin

; --------------------------------------------------------------------- strings
; NOTE: the generic `(string) @string` fallback lives at the BOTTOM of this file
; so more specific same-span rules (quoted object keys, etc.) take priority.
(escape_sequence) @string.escape

; interpolation:  {{ expr | filter }}
(interpolation_start) @punctuation.special
(interpolation_end) @punctuation.special
(interpolation (identifier) @variable.interpolation)
(interpolation (member_expression (identifier) @variable.interpolation))
(filter "|" @function.method)
(filter name: (identifier) @function.method)

; liquid directives:  {% for x in y %}
(directive_start) @tag.delimiter
(directive_end) @tag.delimiter
(directive_keyword) @keyword.directive

; ----------------------------------------------------------------- annotations
(annotation "#" @attribute)
(annotation name: (identifier) @attribute)

; ------------------------------------------------------------------- speakers
; Capture the whole tag AND its inner name as @label, so the narrower inner
; identifier doesn't fall through to the generic @variable rule.
(speaker_tag) @label
(speaker_tag (identifier) @label)

; --------------------------------------------------------------------- types
(primitive_type) @type.builtin
(type_identifier) @type
(type_declaration name: (type_identifier) @type)
(subtype (identifier) @type)
; `import type Foo from ...` — the imported names are types when the `type`
; keyword is present (matched via the type_kw field).
(import_statement type_kw: _ name: (identifier) @type)

; ----------------------------------------------------------------- functions
(function_declaration name: (identifier) @function)
(call_expression function: (identifier) @function.call)
(method_call method: (identifier) @function.call)
(closure_call function: (identifier) @function.call)
(range_expression "range" @function.builtin)

; ----------------------------------------------------------------- parameters
(parameter name: (identifier) @variable.parameter)

; ------------------------------------------------------- properties / members
(member_expression property: (property_identifier) @property)
(pair key: (property_identifier) @property)
(pair key: (string) @property)
(struct_field name: (property_identifier) @property)
(named_argument name: (identifier) @property)

; ------------------------------------------------------------------- keywords
(break_statement) @keyword
(continue_statement) @keyword

[
  "if" "else" "for" "while" "do" "in"
  "return" "jump" "throw" "map"
] @keyword

[
  "let" "const" "function" "type" "import" "from"
] @keyword.declaration

[
  "is" "as"
] @keyword.operator

; ------------------------------------------------------------------- operators
[
  "+" "-" "*" "/" "%"
  "==" "!=" "<" "<=" ">" ">="
  "&&" "||" "!" "??"
  "?" ":" "="
] @operator

; ------------------------------------------------------------ generic fallbacks
; Listed LAST so any more-specific same-span capture above wins. A bare string
; is @string; a bare identifier is @variable.
(string) @string
(identifier) @variable
