{{- define "three-tier-app.name" -}}
three-tier-app
{{- end }}

{{- define "three-tier-app.fullname" -}}
{{ include "three-tier-app.name" . }}
{{- end }}