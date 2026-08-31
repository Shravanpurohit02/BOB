from .application_composition import (
    ApplicationCompositionEngine,
    ApplicationCompositionError,
    ApplicationCompositionMapping,
    ApplicationCompositionRequest,
    ApplicationCompositionResult,
    application_composition,
)

from .composition import (
    CodeLibraryCompositionEngine,
    CodeLibraryCompositionError,
    CompositionRequest,
    CompositionResult,
    composition,
)

from .catalog import (
    CodeLibraryCatalog,
    CodeLibraryCatalogEngine,
    CodeLibraryCatalogEntry,
    catalog,
)
from .engine import CodeLibraryEngine, engine
from .outcomes import CodeAssetOutcome
from .models import (
    CodeAsset,
    CodeAssetFile,
    CodeAssetProvenance,
    CodeAssetRelationship,
    CodeAssetType,
    CodeAssetVersion,
    CodeAssetLifecycle,
    CodeAssetUsage,
)
from .store import CodeLibraryStore


















from .knowledge_integration import (
    KnowledgeRecord,
    KnowledgeIntegrationResult,
    CodeLibraryKnowledgeIntegrator,
    CodeLibraryKnowledgeRecord,
    CodeLibraryKnowledgeIntegrationResult,
)

from .version_preference import (
    CodeAssetVersionPreference,
    CodeAssetVersionSelection,
    CodeLibraryVersionPreference,
    version_preference,
)

from .supersession import (
    CodeAssetSupersessionDecision,
    CodeLibrarySupersessionManager,
    supersession_manager,
)

from .conflict_detection import (
    CodeAssetConflict,
    CodeAssetConflictReport,
    CodeLibraryConflictDetector,
    conflict_detector,
)

from .deprecation import (
    CodeAssetDeprecationDecision,
    CodeLibraryDeprecationManager,
    deprecation_manager,
)

from .demotion import (
    CodeAssetDemotionDecision,
    CodeLibraryDemotionRules,
    demotion_rules,
)

from .trusted_templates import (
    CodeAssetTrustDecision,
    CodeLibraryTrustedTemplateRegistry,
    trusted_templates,
)

from .promotion import (
    CodeAssetPromotionDecision,
    CodeLibraryPromotionRules,
    promotion_rules,
)

from .reliability_scoring import (
    CodeAssetReliabilityScore,
    CodeLibraryReliabilityScorer,
    reliability_scorer,
)

from .quality_scoring import (
    CodeAssetQualityScore,
    CodeLibraryQualityScorer,
    quality_scorer,
)

from .success_detection import (
    CodeAssetSuccessProfile,
    CodeLibrarySuccessDetector,
    success_detector,
)

from .success_rates import (
    CodeAssetSuccessRate,
    CodeLibrarySuccessRateCalculator,
    success_rate_calculator,
)

from .reuse_tracking import (
    CodeAssetReuseEvent,
    CodeAssetReuseSummary,
    CodeLibraryReuseTracker,
    reuse_tracker,
)

from .validation_tracking import (
    CodeAssetValidationEvent,
    CodeAssetValidationSummary,
    CodeLibraryValidationTracker,
    validation_tracker,
)

from .repair_tracking import (
    CodeAssetRepairEvent,
    CodeAssetRepairSummary,
    CodeLibraryRepairTracker,
    repair_tracker,
)

from .build_failures import (
    CodeAssetBuildFailure,
    CodeAssetBuildFailureSummary,
    CodeLibraryFailedBuildTracker,
    failed_build_tracker,
)

from .build_outcomes import (
    CodeAssetBuildSuccess,
    CodeAssetBuildSuccessSummary,
    CodeLibrarySuccessfulBuildTracker,
    successful_build_tracker,
)

from .usage import (
    CodeAssetUsageStage,
    CodeAssetUsageEvent,
    CodeAssetUsageSummary,
    CodeLibraryUsageTracker,
    usage_tracker,
)
from .retrieval import (
    CodeLibraryRetrievalEngine,
    CodeLibraryRetrievalItem,
    CodeLibraryRetrievalResult,
    retrieval,
)

__all__ = (
    "CodeAsset",
    "CodeAssetOutcome",
    "CodeAssetFile",
    "CodeAssetLifecycle",
    "CodeAssetProvenance",
    "CodeAssetRelationship",
    "CodeAssetType",
    "CodeAssetUsage",
    "CodeAssetVersion",
    "CodeLibraryCatalog",
    "CodeLibraryCatalogEngine",
    "CodeLibraryCatalogEntry",
    "CodeLibraryEngine",
    "CodeLibraryStore",
    "CodeLibraryRetrievalEngine",
    "CodeLibraryRetrievalItem",
    "CodeLibraryRetrievalResult",
    "retrieval",
    "catalog",
    "engine",
)

__all__ = (*__all__, "CodeLibraryCompositionEngine")

__all__ = (*__all__, "CodeLibraryCompositionError")

__all__ = (*__all__, "CompositionRequest")

__all__ = (*__all__, "CompositionResult")

__all__ = (*__all__, "composition")

# CL-6 public export: ApplicationCompositionEngine

# CL-6 public export: ApplicationCompositionError

# CL-6 public export: ApplicationCompositionMapping

# CL-6 public export: ApplicationCompositionRequest

# CL-6 public export: ApplicationCompositionResult

# CL-6 public export: application_composition

__all__ = (*__all__, "CodeAssetUsageStage")
__all__ = (*__all__, "CodeAssetUsageEvent")
__all__ = (*__all__, "CodeAssetUsageSummary")
__all__ = (*__all__, "CodeLibraryUsageTracker")
__all__ = (*__all__, "usage_tracker")

__all__ = (*__all__, "CodeAssetBuildSuccess")
__all__ = (*__all__, "CodeAssetBuildSuccessSummary")
__all__ = (*__all__, "CodeLibrarySuccessfulBuildTracker")
__all__ = (*__all__, "successful_build_tracker")

__all__ = (*__all__, "CodeAssetBuildFailure")
__all__ = (*__all__, "CodeAssetBuildFailureSummary")
__all__ = (*__all__, "CodeLibraryFailedBuildTracker")
__all__ = (*__all__, "failed_build_tracker")

__all__ = (*__all__, "CodeAssetRepairEvent")
__all__ = (*__all__, "CodeAssetRepairSummary")
__all__ = (*__all__, "CodeLibraryRepairTracker")
__all__ = (*__all__, "repair_tracker")

__all__ = (*__all__, "CodeAssetValidationEvent")
__all__ = (*__all__, "CodeAssetValidationSummary")
__all__ = (*__all__, "CodeLibraryValidationTracker")
__all__ = (*__all__, "validation_tracker")

__all__ = (*__all__, "CodeAssetReuseEvent")
__all__ = (*__all__, "CodeAssetReuseSummary")
__all__ = (*__all__, "CodeLibraryReuseTracker")
__all__ = (*__all__, "reuse_tracker")

__all__ = (*__all__, "CodeAssetSuccessRate")
__all__ = (*__all__, "CodeLibrarySuccessRateCalculator")
__all__ = (*__all__, "success_rate_calculator")

__all__ = (*__all__, "CodeAssetSuccessProfile")
__all__ = (*__all__, "CodeLibrarySuccessDetector")
__all__ = (*__all__, "success_detector")

__all__ = (*__all__, "CodeAssetQualityScore")
__all__ = (*__all__, "CodeLibraryQualityScorer")
__all__ = (*__all__, "quality_scorer")

__all__ = (*__all__, "CodeAssetReliabilityScore")
__all__ = (*__all__, "CodeLibraryReliabilityScorer")
__all__ = (*__all__, "reliability_scorer")

__all__ = (*__all__, "CodeAssetPromotionDecision")
__all__ = (*__all__, "CodeLibraryPromotionRules")
__all__ = (*__all__, "promotion_rules")

__all__ = (*__all__, "CodeAssetTrustDecision")
__all__ = (*__all__, "CodeLibraryTrustedTemplateRegistry")
__all__ = (*__all__, "trusted_templates")

__all__ = (*__all__, "CodeAssetDemotionDecision")
__all__ = (*__all__, "CodeLibraryDemotionRules")
__all__ = (*__all__, "demotion_rules")

__all__ = (*__all__, "CodeAssetDeprecationDecision")
__all__ = (*__all__, "CodeLibraryDeprecationManager")
__all__ = (*__all__, "deprecation_manager")

__all__ = (*__all__, "CodeAssetConflict")
__all__ = (*__all__, "CodeAssetConflictReport")
__all__ = (*__all__, "CodeLibraryConflictDetector")
__all__ = (*__all__, "conflict_detector")

__all__ = (*__all__, "CodeAssetSupersessionDecision")
__all__ = (*__all__, "CodeLibrarySupersessionManager")
__all__ = (*__all__, "supersession_manager")

__all__ = (*__all__, "CodeAssetVersionPreference")
__all__ = (*__all__, "CodeAssetVersionSelection")
__all__ = (*__all__, "CodeLibraryVersionPreference")
__all__ = (*__all__, "version_preference")

__all__ = (*__all__, "CodeLibraryKnowledgeRecord")
__all__ = (*__all__, "CodeLibraryKnowledgeIntegration")
__all__ = (*__all__, "knowledge_integration")

from .native_assets import (
    BOBNativeAssetDefinition,
    BOBNativeAssetRegistry,
    native_assets,
)

__all__ = (*__all__, "BOBNativeAssetDefinition")
__all__ = (*__all__, "BOBNativeAssetRegistry")
__all__ = (*__all__, "native_assets")

from .open_source_assets import (
    OpenSourceAssetDefinition,
    OpenSourceAssetRegistry,
    open_source_assets,
)

__all__ = (*__all__, "OpenSourceAssetDefinition")
__all__ = (*__all__, "OpenSourceAssetRegistry")
__all__ = (*__all__, "open_source_assets")

from .application_templates import (
    ApplicationTemplateDefinition,
    ApplicationTemplateRegistry,
    application_templates,
)

__all__ = (*__all__, "ApplicationTemplateDefinition")
__all__ = (*__all__, "ApplicationTemplateRegistry")
__all__ = (*__all__, "application_templates")

from .saas_templates import (
    SaaSTemplateDefinition,
    SaaSTemplateRegistry,
    saas_templates,
)

__all__ = (*__all__, "SaaSTemplateDefinition")
__all__ = (*__all__, "SaaSTemplateRegistry")
__all__ = (*__all__, "saas_templates")

from .admin_dashboards import (
    AdminDashboardDefinition,
    AdminDashboardRegistry,
    admin_dashboards,
)

__all__ = (*__all__, "AdminDashboardDefinition")
__all__ = (*__all__, "AdminDashboardRegistry")
__all__ = (*__all__, "admin_dashboards")

from .crm_assets import (
    CRMAssetDefinition,
    CRMAssetRegistry,
    crm_assets,
)

__all__ = (*__all__, "CRMAssetDefinition")
__all__ = (*__all__, "CRMAssetRegistry")
__all__ = (*__all__, "crm_assets")

from .ecommerce_assets import (
    EcommerceAssetDefinition,
    EcommerceAssetRegistry,
    ecommerce_assets,
)

__all__ = (*__all__, "EcommerceAssetDefinition")
__all__ = (*__all__, "EcommerceAssetRegistry")
__all__ = (*__all__, "ecommerce_assets")

from .auth_assets import (
    AuthAssetDefinition,
    AuthAssetRegistry,
    auth_assets,
)

__all__ = (*__all__, "AuthAssetDefinition")
__all__ = (*__all__, "AuthAssetRegistry")
__all__ = (*__all__, "auth_assets")

from .payment_billing_assets import (
    PaymentBillingAssetDefinition,
    PaymentBillingAssetRegistry,
    payment_billing_assets,
)

__all__ = (*__all__, "PaymentBillingAssetDefinition")
__all__ = (*__all__, "PaymentBillingAssetRegistry")
__all__ = (*__all__, "payment_billing_assets")

from .notification_messaging_assets import (
    NotificationMessagingAssetDefinition,
    NotificationMessagingAssetRegistry,
    notification_messaging_assets,
)

__all__ = (*__all__, "NotificationMessagingAssetDefinition")
__all__ = (*__all__, "NotificationMessagingAssetRegistry")
__all__ = (*__all__, "notification_messaging_assets")

from .recommendation import (
    CodeAssetRecommendation,
    CodeAssetRecommendationRequest,
    CodeLibraryRecommendationEngine,
    recommendation,
)

__all__ = (*__all__, "CodeAssetRecommendation")
__all__ = (*__all__, "CodeAssetRecommendationRequest")
__all__ = (*__all__, "CodeLibraryRecommendationEngine")
__all__ = (*__all__, "recommendation")

from .context_recommendation import (
    AssetRecommendationContext,
    ContextAwareRecommendationEngine,
    context_recommendation,
)

__all__ = (*__all__, "AssetRecommendationContext")
__all__ = (*__all__, "ContextAwareRecommendationEngine")
__all__ = (*__all__, "context_recommendation")

from .compatibility import (
    AssetCompatibilityContext,
    AssetCompatibilityScore,
    CodeLibraryCompatibilityEngine,
    compatibility,
)

__all__ = (*__all__, "AssetCompatibilityContext")
__all__ = (*__all__, "AssetCompatibilityScore")
__all__ = (*__all__, "CodeLibraryCompatibilityEngine")
__all__ = (*__all__, "compatibility")

from .dependency_compatibility import (
    DependencyCompatibilityContext,
    DependencyCompatibilityResult,
    CodeLibraryDependencyCompatibilityEngine,
    dependency_compatibility,
)

__all__ = (*__all__, "DependencyCompatibilityContext")
__all__ = (*__all__, "DependencyCompatibilityResult")
__all__ = (*__all__, "CodeLibraryDependencyCompatibilityEngine")
__all__ = (*__all__, "dependency_compatibility")

from .conflict_analysis import (
    AssetConflictContext,
    AssetConflictResult,
    CodeLibraryConflictAnalysisEngine,
    conflict_analysis,
)

__all__ = (*__all__, "AssetConflictContext")
__all__ = (*__all__, "AssetConflictResult")
__all__ = (*__all__, "CodeLibraryConflictAnalysisEngine")
__all__ = (*__all__, "conflict_analysis")

from .composition_compatibility import (
    CompositionContext,
    CompositionCompatibilityResult,
    CodeLibraryCompositionCompatibilityEngine,
    composition_compatibility,
)

__all__ = (*__all__, "CompositionContext")
__all__ = (*__all__, "CompositionCompatibilityResult")
__all__ = (*__all__, "CodeLibraryCompositionCompatibilityEngine")
__all__ = (*__all__, "composition_compatibility")

from .dependency_graph import (
    DependencyGraphContext,
    DependencyGraphNode,
    DependencyGraphResult,
    CodeLibraryDependencyGraphEngine,
    dependency_graph,
)

__all__ = (*__all__, "DependencyGraphContext")
__all__ = (*__all__, "DependencyGraphNode")
__all__ = (*__all__, "DependencyGraphResult")
__all__ = (*__all__, "CodeLibraryDependencyGraphEngine")
__all__ = (*__all__, "dependency_graph")

from .dependency_impact import (
    DependencyImpactResult,
    CodeLibraryDependencyImpactEngine,
    dependency_impact,
)

__all__ = (*__all__, "DependencyImpactResult")
__all__ = (*__all__, "CodeLibraryDependencyImpactEngine")
__all__ = (*__all__, "dependency_impact")

from .change_impact import (
    AssetChangeContext,
    AssetChangeImpactResult,
    CodeLibraryChangeImpactEngine,
    change_impact,
)

__all__ = (*__all__, "AssetChangeContext")
__all__ = (*__all__, "AssetChangeImpactResult")
__all__ = (*__all__, "CodeLibraryChangeImpactEngine")
__all__ = (*__all__, "change_impact")

from .compatibility_decision import (
    CompatibilityDecision,
    CodeLibraryCompatibilityDecisionEngine,
    compatibility_decision,
)

__all__ = (*__all__, "CompatibilityDecision")
__all__ = (*__all__, "CodeLibraryCompatibilityDecisionEngine")
__all__ = (*__all__, "compatibility_decision")

from .composition_planning import (
    CompositionPlanContext,
    CompositionPlanItem,
    CompositionPlan,
    CodeLibraryCompositionPlanningEngine,
    composition_planning,
)

__all__ = (*__all__, "CompositionPlanContext")
__all__ = (*__all__, "CompositionPlanItem")
__all__ = (*__all__, "CompositionPlan")
__all__ = (*__all__, "CodeLibraryCompositionPlanningEngine")
__all__ = (*__all__, "composition_planning")

from .assembly_planning import (
    AssemblyUnit,
    AssemblyPlan,
    CodeLibraryAssemblyPlanningEngine,
    assembly_planning,
)

__all__ = (*__all__, "AssemblyUnit")
__all__ = (*__all__, "AssemblyPlan")
__all__ = (*__all__, "CodeLibraryAssemblyPlanningEngine")
__all__ = (*__all__, "assembly_planning")
from .compatibility_learning import (
    CompatibilityLearningContext,
    CompatibilityLearningResult,
    CompatibilityObservation,
    CodeLibraryCompatibilityLearningEngine,
)

from .combination_learning import (
    CombinationLearningContext,
    CombinationLearningResult,
    CombinationObservation,
    CodeLibraryCombinationLearningEngine,
)

from .application_stacks import (
    ApplicationStackContext,
    ApplicationStackResult,
    ApplicationStackObservation,
    CodeLibraryApplicationStackEngine,
)

from .architecture_recommendations import (
    ArchitectureRecommendationContext,
    ArchitectureRecommendation,
    CodeLibraryArchitectureRecommendationEngine,
)

from .technology_combination_learning import (
    TechnologyCombinationContext,
    TechnologyCombinationObservation,
    TechnologyCombinationResult,
    CodeLibraryTechnologyCombinationLearningEngine,
)

from .project_adaptation_learning import (
    ProjectAdaptationContext,
    ProjectAdaptationObservation,
    ProjectAdaptationResult,
    CodeLibraryProjectAdaptationLearningEngine,
)

from .android_packaging import (
    AndroidPackagingContext,
    AndroidPackageArtifact,
    AndroidPackagingPlan,
    CodeLibraryAndroidPackagingEngine,
)

from .offline_catalog import (
    OfflineCatalogContext,
    OfflineCatalogEntry,
    OfflineCatalogResult,
    CodeLibraryOfflineCatalog,
)

from .local_storage import (
    LocalStorageContext,
    LocalStorageRecord,
    CodeLibraryLocalStorage,
)

from .local_retrieval import (
    LocalRetrievalQuery,
    LocalRetrievalCandidate,
    LocalRetrievalResult,
    CodeLibraryLocalRetrievalEngine,
)

from .resource_index import (
    ResourceIndexEntry,
    ResourceIndexResult,
    CodeLibraryResourceIndex,
)

from .incremental_updates import (
    IncrementalUpdate,
    IncrementalUpdateResult,
    CodeLibraryIncrementalUpdater,
)

from .android_compatibility import (
    AndroidCompatibilityContext,
    AndroidCompatibilityResult,
    CodeLibraryAndroidCompatibilityEngine,
)

from .compiled_payload_verification import (
    CompiledPayloadManifest,
    CompiledPayloadVerificationResult,
    CodeLibraryCompiledPayloadVerifier,
)

from .integration_verification import (
    CodeLibraryIntegrationResult,
    CodeLibraryIntegrationVerifier,
)

from .requirement_understanding import (
    ConstructionRequirement,
    RequirementUnderstandingResult,
    CodeLibraryRequirementUnderstanding,
)

from .retrieval_integration import (
    RequirementRetrievalResult,
    CodeLibraryRequirementRetrieval,
)

from .asset_selection import (
    AssetSelectionResult,
    CodeLibraryAssetSelector,
)

from .architecture_composition import (
    ArchitectureUnit,
    ArchitectureCompositionResult,
    CodeLibraryArchitectureComposer,
)

from .construction_plan import (
    ConstructionStep,
    ConstructionPlanResult,
    CodeLibraryConstructionPlanner,
)

from .repository_intelligence import (
    RepositoryFile,
    RepositoryIntelligenceResult,
    CodeLibraryRepositoryIntelligence,
)

from .code_generation_integration import (
    GenerationRequest,
    GenerationIntegrationResult,
    CodeLibraryCodeGenerationIntegration,
)

from .execution_integration import (
    ExecutionResult,
    ExecutionIntegrationResult,
    CodeLibraryExecutionIntegration,
)

from .execution_result_verification import (
    VerificationResult,
    ExecutionVerificationResult,
    CodeLibraryExecutionResultVerifier,
)

from .repair_replanning import (
    RepairAction,
    RepairPlan,
    CodeLibraryRepairReplanner,
)

from .outcome_learning import (
    OutcomeSignal,
    OutcomeLearningResult,
    CodeLibraryOutcomeLearner,
)

from .knowledge_integration import (
    KnowledgeRecord,
    KnowledgeIntegrationResult,
    CodeLibraryKnowledgeIntegrator,
)

from .future_construction import (
    FutureConstructionAdjustment,
    FutureConstructionResult,
    CodeLibraryFutureConstruction,
)
