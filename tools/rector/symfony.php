<?php
use Rector\Config\RectorConfig;
use Rector\Symfony\Rector\Class_\ServiceDefinitionToAttributeRector;
use Rector\Transform\Rector\MethodCall\MethodCallRector;
use Rector\Transform\ValueObject\MethodCallRename;
use Rector\Symfony\Rector\Class_\AnnotationToAttributeRector;
use Rector\Transform\Rector\FileContentRector;
use Rector\Transform\ValueObject\StringReplace;

return static function (RectorConfig $rectorConfig): void {
    // Règles pour migrer vers Symfony 6
    $rectorConfig->sets([\Rector\Symfony\Set\SymfonySetList::SYMFONY_60]);

    // Règle pour migrer les définitions de services YAML/XML vers des attributs PHP
    $rectorConfig->rule(ServiceDefinitionToAttributeRector::class);

    // Règle pour migrer les bundles (ex. : Kernel::registerBundles)
    $rectorConfig->ruleWithConfiguration(
        MethodCallRector::class,
        [
            new MethodCallRename(
                'App\Kernel',
                'registerBundles',
                'App\Kernel::registerModernBundles'
            ),
        ]
    );

    // Règle pour migrer les routes (ex. : @Route vers #[Route])
    $rectorConfig->ruleWithConfiguration(
        AnnotationToAttributeRector::class,
        [
            new \Rector\Symfony\ValueObject\AnnotationToAttribute(
                'Symfony\Component\Routing\Annotation\Route',
                'Symfony\Component\Routing\Attribute\Route'
            ),
        ]
    );

    // Règle pour migrer les entités Doctrine (ex. : annotations vers attributs)
    $rectorConfig->ruleWithConfiguration(
        AnnotationToAttributeRector::class,
        [
            new \Rector\Symfony\ValueObject\AnnotationToAttribute(
                'Doctrine\ORM\Mapping\Entity',
                'Doctrine\ORM\Mapping\Attribute\Entity'
            ),
        ]
    );

    // Règle pour migrer les configurations (ex. : YAML vers PHP)
    $rectorConfig->ruleWithConfiguration(
        FileContentRector::class,
        [
            new StringReplace(
                'parameters:\n\s+app\.locale:\s+\'([^\']+)\'',
                'public const APP_LOCALE = \'$1\';'
            ),
        ]
    );

    // Chemins à analyser
    $rectorConfig->paths([__DIR__ . '/../../backend/app']);
};