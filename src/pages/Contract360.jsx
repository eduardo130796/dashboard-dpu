import React from 'react';
import { useData } from '@/lib/DataContext';
import { getDaysRemaining, formatCurrency, formatCompactCurrency, getCriticalityConfig, getStatusConfig, getRiskColor } from '@/lib/contractUtils';
import { StatusBadge, CriticalityBadge } from '@/components/shared/StatusBadge';
import RiskScoreBar from '@/components/shared/RiskScoreBar';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { format, parseISO } from 'date-fns';
import { ArrowLeft, Building2, Calendar, User, DollarSign, Shield, Loader2 } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { cn } from '@/lib/utils';

export default function Contract360() {
  const { contractNumber: rawParam } = useParams();
  const contractNumber = rawParam ? decodeURIComponent(rawParam) : rawParam;
  const { contracts } = useData();

  const detailLoading = false;

  const contract = contracts.find(c => c.contract_number === contractNumber);
  const { amendments, events, alerts: allAlerts } = useData();
  const contractAmendments = amendments.filter(a => a.contract_number === contractNumber);
  const contractEvents     = events.filter(e => e.contract_number === contractNumber)
    .sort((a, b) => new Date(b.event_date) - new Date(a.event_date));
  const contractAlerts     = allAlerts.filter(a => a.contract_number === contractNumber);

  if (!contract && !detailLoading) {
    return (
      <div className="p-6 text-center">
        <p className="text-muted-foreground">Contrato não encontrado.</p>
        <Link to="/contracts" className="text-primary text-sm hover:underline">Voltar aos contratos</Link>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="p-6 flex items-center justify-center gap-3 text-muted-foreground">
        <Loader2 className="w-5 h-5 animate-spin" />
        <span className="text-sm">Carregando dados do contrato…</span>
      </div>
    );
  }

  const days        = getDaysRemaining(contract.end_date);
  const healthScore = Math.max(0, 100 - (contract.risk_score || 0));
  const financial   = null;
  const scope       = [];

  return (
    <div className="p-4 lg:p-6 space-y-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div>
        <Link to="/contracts" className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-3">
          <ArrowLeft className="w-4 h-4" /> Voltar aos Contratos
        </Link>
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-xl font-bold text-foreground">{contract.contract_number}</h1>
              <StatusBadge status={contract.status} />
              <CriticalityBadge criticality={contract.criticality} />
              {detailLoading && <Loader2 className="w-4 h-4 text-muted-foreground animate-spin" />}
            </div>
            <p className="text-sm text-muted-foreground">{contract.object}</p>
          </div>
          <div className="flex items-center gap-6">
            <div className="text-center">
              <div className={cn("text-3xl font-bold tabular-nums", healthScore >= 60 ? 'text-emerald-500' : healthScore >= 40 ? 'text-amber-400' : 'text-red-500')}>
                {healthScore}
              </div>
              <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Saúde</div>
            </div>
            <div className="text-center">
...
              <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Dias Restantes</div>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <InfoCard icon={Building2} label="Fornecedor" value={contract.contractor} />
        <InfoCard icon={User}      label="Gestor"    value={contract.manager !== '—' ? contract.manager : (detailLoading ? '…' : '—')} />
        <InfoCard icon={DollarSign} label="Valor"     value={formatCurrency(contract.value)} />
        <InfoCard icon={Calendar}  label="Início"      value={contract.start_date ? format(parseISO(contract.start_date), 'dd/MM/yyyy') : '—'} />
        <InfoCard icon={Calendar}  label="Fim"        value={contract.end_date   ? format(parseISO(contract.end_date),   'dd/MM/yyyy') : '—'} />
        <InfoCard icon={Shield}    label="Pontuação de Risco" value={`${contract.risk_score}/100`} />
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview">
        <TabsList className="bg-accent/50">
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="timeline">Histórico</TabsTrigger>
          <TabsTrigger value="risks">Riscos</TabsTrigger>
          <TabsTrigger value="amendments">Aditivos</TabsTrigger>
          <TabsTrigger value="actions">Ações</TabsTrigger>
        </TabsList>

        {/* ── OVERVIEW ── */}
        <TabsContent value="overview" className="mt-4 space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-card border border-border rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-semibold">Detalhes do Contrato</h3>
              <div className="space-y-3">
                <DetailRow label="Categoria"          value={contract.category} />
                <DetailRow label="Unidade"              value={contract.unit} />
                <DetailRow label="Modalidade"        value={contract._modalidade || '—'} />
                <DetailRow label="Processo"          value={contract._processo || '—'} />
                <DetailRow label="Situação"          value={contract._situacao || '—'} />
                <DetailRow label="Impacto Operacional" value={contract.operational_impact} />
                <DetailRow label="Risco de Continuidade"   value={contract.continuity_risk} />
                <DetailRow label="Estratégico"         value={contract.is_strategic ? 'Sim' : 'Não'} />
                <DetailRow label="Aditivos"        value={String(contract.amendments_count)} />
              </div>
            </div>

            <div className="bg-card border border-border rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-semibold">Suporte à Decisão</h3>
              <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
                <p className="text-xs font-medium text-primary mb-1">Ação Recomendada</p>
                <p className="text-sm text-foreground">{contract.recommended_action}</p>
              </div>
              <div className="space-y-3">
                <DetailRow label="Pontuação de Risco"   value={<RiskScoreBar score={contract.risk_score} />} />
                <DetailRow label="Vencimento"   value={days !== null ? (days > 0 ? `${days} dias restantes` : 'Vencido') : '—'} />
                <DetailRow label="Alertas Ativos" value={String(contractAlerts.filter(a => a.status === 'active').length)} />
              </div>

              {/* Financial summary from empenhos */}
              {financial && (
                <div className="mt-3 space-y-2 border-t border-border pt-3">
                  <p className="text-xs font-semibold text-muted-foreground uppercase">Execução Financeira</p>
                  <DetailRow label="Empenhado"  value={formatCompactCurrency(financial.totalEmpenhado)} />
                  <DetailRow label="Liquidado"  value={formatCompactCurrency(financial.totalLiquidado)} />
                  <DetailRow label="Pago"       value={formatCompactCurrency(financial.totalPago)} />
                </div>
              )}
            </div>
          </div>

          {/* Scope items */}
          {scope.length > 0 && (
            <div className="bg-card border border-border rounded-xl p-5">
              <h3 className="text-sm font-semibold mb-3">Escopo / Itens</h3>
              <div className="space-y-2">
                {scope.map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-2.5 rounded-lg bg-accent/30">
                    <span className="text-xs text-foreground">{item.description}</span>
                    <span className="text-xs font-medium text-foreground">{formatCurrency(item.total)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </TabsContent>

        {/* ── TIMELINE ── */}
        <TabsContent value="timeline" className="mt-4">
          <div className="bg-card border border-border rounded-xl p-5">
            <h3 className="text-sm font-semibold mb-4">Linha do Tempo</h3>
            {detailLoading && contractEvents.length === 0 ? (
              <div className="flex items-center gap-2 text-muted-foreground text-sm">
                <Loader2 className="w-4 h-4 animate-spin" /> Carregando histórico…
              </div>
            ) : contractEvents.length === 0 ? (
              <p className="text-sm text-muted-foreground">Nenhum evento registrado.</p>
            ) : (
              <div className="space-y-0">
                {contractEvents.map((event, i) => (
                  <div key={i} className="flex gap-3 pb-4 last:pb-0">
                    <div className="flex flex-col items-center">
                      <div className="w-2.5 h-2.5 rounded-full bg-primary mt-1.5 shrink-0" />
                      {i < contractEvents.length - 1 && <div className="w-px flex-1 bg-border mt-1" />}
                    </div>
                    <div className="pb-2">
                      <p className="text-sm font-medium text-foreground">{event.title}</p>
                      <p className="text-xs text-muted-foreground">{event.description}</p>
                      <div className="flex items-center gap-2 mt-1">
                        {event.event_date && (
                          <span className="text-[10px] text-muted-foreground">
                            {format(parseISO(event.event_date), 'dd/MM/yyyy')}
                          </span>
                        )}
                        {event.actor && <span className="text-[10px] text-muted-foreground">por {event.actor}</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </TabsContent>

        {/* ── RISKS ── */}
        <TabsContent value="risks" className="mt-4">
          <div className="bg-card border border-border rounded-xl p-5 space-y-4">
            <h3 className="text-sm font-semibold">Avaliação de Risco</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <RiskFactorCard label="Proximidade do Vencimento" value={days !== null && days <= 30 ? 'Alto' : days !== null && days <= 90 ? 'Médio' : 'Baixo'} />
              <RiskFactorCard label="Impacto Operacional"   value={contract.operational_impact} />
              <RiskFactorCard label="Risco de Continuidade"      value={contract.continuity_risk} />
              <RiskFactorCard label="Histórico de Aditivos"    value={contract.amendments_count > 3 ? 'Elevado' : 'Normal'} />
            </div>
            {contractAlerts.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground uppercase mb-2">Alertas Ativos</h4>
                {contractAlerts.map((alert, i) => (
                  <div key={i} className="flex items-center gap-3 p-2.5 rounded-lg bg-accent/30 mb-1.5">
                    <span className={cn("w-2 h-2 rounded-full shrink-0",
                      alert.severity === 'red'    ? 'bg-red-500' :
                      alert.severity === 'orange' ? 'bg-orange-500' : 'bg-amber-400'
                    )} />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium">{alert.title}</p>
                      <p className="text-[10px] text-muted-foreground truncate">{alert.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </TabsContent>

        {/* ── AMENDMENTS ── */}
        <TabsContent value="amendments" className="mt-4">
          <div className="bg-card border border-border rounded-xl p-5">
            <h3 className="text-sm font-semibold mb-4">Histórico de Aditivos ({contractAmendments.length})</h3>
            {detailLoading && contractAmendments.length === 0 ? (
              <div className="flex items-center gap-2 text-muted-foreground text-sm">
                <Loader2 className="w-4 h-4 animate-spin" /> Carregando aditivos…
              </div>
            ) : contractAmendments.length === 0 ? (
              <p className="text-sm text-muted-foreground">Nenhum aditivo registrado.</p>
            ) : (
              <div className="space-y-2">
                {contractAmendments.map((amd, i) => (
                  <div key={i} className="p-3 rounded-lg border border-border bg-accent/20">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-medium">{amd.amendment_number}</span>
                      <Badge variant="secondary" className="text-[10px] capitalize">{amd.status}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{amd.description}</p>
                    <div className="flex items-center gap-3 mt-2 text-[10px] text-muted-foreground">
                      <span>Tipo: {amd.type}</span>
                      {amd.effective_date && (
                        <span>Data: {format(parseISO(amd.effective_date), 'dd/MM/yyyy')}</span>
                      )}
                      {amd.value_change !== 0 && <span>Variação: {formatCurrency(amd.value_change)}</span>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </TabsContent>

        {/* ── ACTIONS ── */}
        <TabsContent value="actions" className="mt-4">
          <div className="bg-card border border-border rounded-xl p-5 space-y-4">
            <h3 className="text-sm font-semibold">Ações Recomendadas</h3>
            <div className="p-4 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-sm text-foreground">{contract.recommended_action}</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <ActionCard title="Revisar Contrato"           description="Agendar análise abrangente com o gestor do contrato e as partes interessadas." />
              <ActionCard title="Avaliar Opções de Renovação" description="Avaliar renovação versus nova licitação com base nas condições atuais do mercado." />
              <ActionCard title="Mitigação de Risco"         description="Implementar estratégias de mitigação com base na avaliação de risco atual." />
              <ActionCard title="Verificação de Conformidade" description="Verificar todos os requisitos de conformidade e obrigações regulatórias." />
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ─── Sub-components (unchanged signatures) ────────────────────────────────────
function InfoCard({ icon: Icon, label, value }) {
  return (
    <div className="bg-card border border-border rounded-xl p-3">
      <div className="flex items-center gap-1.5 mb-1">
        <Icon className="w-3.5 h-3.5 text-muted-foreground" />
        <span className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</span>
      </div>
      <p className="text-sm font-medium text-foreground truncate">{value}</p>
    </div>
  );
}

function DetailRow({ label, value }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-border/50 last:border-0">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="text-xs font-medium text-foreground capitalize">{typeof value === 'string' ? value : value}</span>
    </div>
  );
}

function RiskFactorCard({ label, value }) {
  const isHigh = ['high', 'critical', 'Elevated', 'High'].includes(value);
  return (
    <div className={cn("p-3 rounded-lg border", isHigh ? 'bg-red-500/5 border-red-500/20' : 'bg-accent/30 border-border')}>
      <p className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</p>
      <p className={cn("text-sm font-semibold mt-0.5 capitalize", isHigh ? 'text-red-500' : 'text-foreground')}>{value}</p>
    </div>
  );
}

function ActionCard({ title, description }) {
  return (
    <div className="p-3 rounded-lg border border-border bg-accent/20 hover:bg-accent/40 transition-colors cursor-pointer">
      <p className="text-sm font-medium text-foreground">{title}</p>
      <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
    </div>
  );
}