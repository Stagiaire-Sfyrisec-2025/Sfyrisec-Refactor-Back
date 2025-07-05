<?php
use Rector\Config\RectorConfig;
use Rector\Symfony\Rector\Class_\ServiceDefinitionToAttributeRector;
use Rector\Transform\Rector\MethodCall\MethodCallRector;
use Rector\Transform\ValueObject\MethodCallRename;

return static function (RectorConfig $rectorConfig): void {
    // Règles pour migrer vers Symfony 6
    $rectorConfig->sets([\Rector\Symfony\Set\SymfonySetList::SYMFONY_60]);

    // Règle pour migrer les définitions de services YAML/XML vers des attributs PHP
    $rectorConfig->rule(ServiceDefinitionToAttributeRector::class);

    // Règle pour migrer les appels dans Kernel::registerBundles
    $rectorConfig->ruleWithConfiguration(
        MethodCallRector::class,
        [
            // Exemple : migrer les appels à un bundle personnalisé
            new MethodCallRename(
                'App\Kernel',
                'registerBundles',
                'App\Kernel::registerModernBundles'
            ),
        ]
    );

    // Chemins à analyser
    $rectorConfig->paths([__DIR__ . '/../../backend/app']);
};