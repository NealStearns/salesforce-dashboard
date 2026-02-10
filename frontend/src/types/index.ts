export interface KPIMetric {
  count: number
  total: number
  average?: number
}

export interface KPISummary {
  open_pipeline: KPIMetric
  won_this_quarter: KPIMetric
  lost_this_quarter: KPIMetric
}

export interface StageData {
  StageName: string
  cnt: number
  total_amount: number
}

export interface PipelineData {
  month: number
  year: number
  total: number
  cnt: number
}

export interface Opportunity {
  Id: string
  Name: string
  StageName: string
  Amount: number | null
  CloseDate: string | null
  Probability: number | null
  Owner: { Name: string } | null
  Account: { Name: string } | null
  Type: string | null
}

export interface OpportunityListResponse {
  records: Opportunity[]
  total: number
  limit: number
  offset: number
}
