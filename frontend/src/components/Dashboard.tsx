import { dashboardApi } from '../services/api'
import { useApi } from '../hooks/useApi'
import KPICard from './KPICard'
import PipelineChart from './PipelineChart'
import StageChart from './StageChart'
import type { KPISummary } from '../types'

export default function Dashboard() {
  const { data: kpis, loading: kpiLoading } = useApi<KPISummary>(
    () => dashboardApi.getKPIs(),
    [],
  )
  const { data: stageData, loading: stageLoading } = useApi(
    () => dashboardApi.getStages(),
    [],
  )
  const { data: pipelineData, loading: pipelineLoading } = useApi(
    () => dashboardApi.getPipeline(),
    [],
  )

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Open Pipeline"
          value={kpis?.open_pipeline.total ?? 0}
          count={kpis?.open_pipeline.count ?? 0}
          format="currency"
          loading={kpiLoading}
          color="blue"
        />
        <KPICard
          title="Avg Deal Size"
          value={kpis?.open_pipeline.average ?? 0}
          format="currency"
          loading={kpiLoading}
          color="purple"
        />
        <KPICard
          title="Won This Quarter"
          value={kpis?.won_this_quarter.total ?? 0}
          count={kpis?.won_this_quarter.count ?? 0}
          format="currency"
          loading={kpiLoading}
          color="green"
        />
        <KPICard
          title="Lost This Quarter"
          value={kpis?.lost_this_quarter.total ?? 0}
          count={kpis?.lost_this_quarter.count ?? 0}
          format="currency"
          loading={kpiLoading}
          color="red"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">
            Pipeline Over Time
          </h3>
          <PipelineChart
            data={pipelineData?.pipeline ?? []}
            loading={pipelineLoading}
          />
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">
            Opportunities by Stage
          </h3>
          <StageChart
            data={stageData?.stages ?? []}
            loading={stageLoading}
          />
        </div>
      </div>
    </div>
  )
}
