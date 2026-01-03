import Button from "../common/Button";
import Card from "../common/Card";
import { refreshHistorical } from "../../services/api";

export default function AdminPanel() {
  const refresh = async () => {
    await refreshHistorical();
    alert("Historical data refreshed");
  };

  return (
    <Card title="Admin Controls">
      <Button onClick={refresh}>Refresh GSheet Data</Button>
    </Card>
  );
}
