def build_alerts(contracts):
    alerts = []

    for c in contracts:
        dias = c.get("daysRemaining")

        # 🔴 Crítico
        if dias is not None and dias <= 30:
            alerts.append({
                "type": "critico",
                "message": f"Contrato {c.get('contract_number')} vence em {dias} dias",
                "contractId": c.get("contract_number"),
                "severity": 3,
                "action": "Iniciar renovação imediatamente"
            })

        # 🔴 Já vencido
        if dias is not None and dias < 0:
            alerts.append({
                "type": "critico",
                "message": f"Contrato {c.get('contract_number')} já está vencido",
                "contractId": c.get("contract_number"),
                "severity": 3,
                "action": "Regularizar ou encerrar imediatamente"
            })

        # 🟡 Atenção
        if dias is not None and 30 < dias <= 60:
            alerts.append({
                "type": "atencao",
                "message": f"Contrato {c.get('contract_number')} vence em breve ({dias} dias)",
                "contractId": c.get("contract_number"),
                "severity": 2,
                "action": "Planejar renovação"
            })

        # 🟡 Sem data
        if dias is None:
            alerts.append({
                "type": "atencao",
                "message": f"Contrato {c.get('contract_number')} sem data de vigência definida",
                "contractId": c.get("contract_number"),
                "severity": 2,
                "action": "Verificar cadastro"
            })

    return sorted(alerts, key=lambda x: x["severity"], reverse=True)