<?php
use Rector\Config\RectorConfig;
use Rector\Transform\Rector\MethodCall\MethodCallRector;
use Rector\Transform\ValueObject\MethodCallRename;
use Rector\Transform\Rector\FileSystem\FileContentRector;
use Rector\Transform\ValueObject\StringReplace;

return static function (RectorConfig $rectorConfig): void {
    // Règles pour migrer CodeIgniter 3 vers CodeIgniter 4
    $rectorConfig->sets([\Rector\CodeIgniter\Set\CodeIgniterLevelSetList::UP_TO_CODEIGNITER_4]);

    // Règle pour migrer les helpers (ex. : $this->load->helper vers helper())
    $rectorConfig->ruleWithConfiguration(
        MethodCallRector::class,
        [
            new MethodCallRename(
                'CI_Controller',
                'load->helper',
                '\CodeIgniter\CodeIgniter::helper'
            ),
        ]
    );

    // Règle pour migrer les sessions (ex. : $this->session->set_userdata vers session()->set)
    $rectorConfig->ruleWithConfiguration(
        MethodCallRector::class,
        [
            new MethodCallRename(
                'CI_Session',
                'set_userdata',
                '\CodeIgniter\Session\Session::set'
            ),
            new MethodCallRename(
                'CI_Session',
                'userdata',
                '\CodeIgniter\Session\Session::get'
            ),
        ]
    );

    // Règle pour migrer les routes (ex. : $route['...'] vers Routes::add)
    $rectorConfig->ruleWithConfiguration(
        FileContentRector::class,
        [
            new StringReplace(
                '$route[\'([^\']+)\'] = \'([^\']+)\';',
                'Routes::add(\'$1\', \'$2\');'
            ),
        ]
    );

    // Règle pour migrer les modèles (ex. : CI_Model vers CodeIgniter\Model)
    $rectorConfig->ruleWithConfiguration(
        FileContentRector::class,
        [
            new StringReplace(
                'extends CI_Model',
                'extends \CodeIgniter\Model'
            ),
        ]
    );

    // Règle pour migrer les configurations (ex. : $config['...'] vers Config\Services)
    $rectorConfig->ruleWithConfiguration(
        FileContentRector::class,
        [
            new StringReplace(
                '$config[\'([^\']+)\'] = ([^;]+);',
                '\CodeIgniter\Config\Services::set(\'$1\', $2);'
            ),
        ]
    );

    // Chemins à analyser
    $rectorConfig->paths([__DIR__ . '/../../backend/app']);
};