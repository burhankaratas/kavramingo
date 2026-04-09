<?php

namespace App\Filament\Resources;

use App\Filament\Resources\QuestionResource\Pages;
use App\Models\Concept;
use App\Models\Question;
use App\Models\Unit;
use App\Support\UnitTopicResolver;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;

class QuestionResource extends Resource
{
    protected static ?string $model = Question::class;

    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';
    protected static ?string $navigationLabel = 'Quiz Sorulari';
    protected static ?string $modelLabel = 'Soru';
    protected static ?string $pluralModelLabel = 'Quiz Sorulari';
    protected static ?string $navigationGroup = 'Icerik';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Select::make('topic_id')
                    ->label('Unite')
                    ->options(
                        Unit::query()
                            ->orderBy('grade')
                            ->orderBy('unit_no')
                            ->get()
                            ->mapWithKeys(fn (Unit $unit) => [
                                $unit->id => $unit->grade . '. Sinif / ' . $unit->unit_no . '. Unite - ' . $unit->name,
                            ])
                            ->all()
                    )
                    ->searchable()
                    ->required(),
                Forms\Components\Select::make('quiz_type')
                    ->label('Quiz Tipi')
                    ->options([
                        'mcq' => 'MCQ',
                        'flashcard' => 'Flashcard',
                        'matching' => 'Matching',
                        'fill_blank' => 'Fill Blank',
                    ])
                    ->live()
                    ->required(),
                Forms\Components\Select::make('difficulty')
                    ->label('Zorluk')
                    ->options([
                        'easy' => 'Kolay',
                        'medium' => 'Orta',
                        'hard' => 'Zor',
                    ])
                    ->required(),
                Forms\Components\TextInput::make('question_code')
                    ->label('Soru Kodu')
                    ->required()
                    ->unique(ignoreRecord: true),
                Forms\Components\Textarea::make('prompt')
                    ->label('Soru Metni')
                    ->rows(3),
                Forms\Components\TextInput::make('order')
                    ->label('Liste Sirasi')
                    ->required()
                    ->numeric()
                    ->default(0),

                Forms\Components\Section::make('MCQ')
                    ->visible(fn (Forms\Get $get) => $get('quiz_type') === 'mcq')
                    ->schema([
                        Forms\Components\TextInput::make('mcq.choice_a')->label('Sik A')->required(),
                        Forms\Components\TextInput::make('mcq.choice_b')->label('Sik B')->required(),
                        Forms\Components\TextInput::make('mcq.choice_c')->label('Sik C')->required(),
                        Forms\Components\TextInput::make('mcq.choice_d')->label('Sik D')->required(),
                        Forms\Components\Select::make('mcq.correct_choice')
                            ->label('Dogru Sik')
                            ->options(['A' => 'A', 'B' => 'B', 'C' => 'C', 'D' => 'D'])
                            ->required(),
                    ])->columns(2),

                Forms\Components\Section::make('Flashcard')
                    ->visible(fn (Forms\Get $get) => $get('quiz_type') === 'flashcard')
                    ->schema([
                        Forms\Components\Textarea::make('flashcard.front_text')->label('On Yuz')->required(),
                        Forms\Components\Textarea::make('flashcard.back_text')->label('Arka Yuz')->required(),
                    ])->columns(1),

                Forms\Components\Section::make('Fill Blank')
                    ->visible(fn (Forms\Get $get) => $get('quiz_type') === 'fill_blank')
                    ->schema([
                        Forms\Components\Textarea::make('fill_blank.sentence_template')
                            ->label('Cumle Sablonu')
                            ->helperText('Bosluk yerine ___ kullanabilirsin.')
                            ->required(),
                        Forms\Components\TextInput::make('fill_blank.answer_text')
                            ->label('Dogru Cevap')
                            ->required(),
                    ]),

                Forms\Components\Section::make('Matching')
                    ->visible(fn (Forms\Get $get) => $get('quiz_type') === 'matching')
                    ->schema([
                        Forms\Components\Repeater::make('matching_pairs')
                            ->label('Eslestirme Ciftleri')
                            ->minItems(3)
                            ->maxItems(6)
                            ->reorderable()
                            ->schema([
                                Forms\Components\TextInput::make('left_text')->label('Sol Metin')->required(),
                                Forms\Components\TextInput::make('right_text')->label('Sag Metin')->required(),
                                Forms\Components\TextInput::make('order')->label('Sira')->numeric()->default(0),
                            ])
                            ->columns(3),
                    ]),

                Forms\Components\Section::make('Kavram Destegi (Opsiyonel)')
                    ->description('Soruya bagli kavram notu eklemek icin kullanilir.')
                    ->schema([
                        Forms\Components\Select::make('concept_id')
                            ->label('Kavram')
                            ->options(
                                Concept::query()
                                    ->with('topic.unit')
                                    ->orderBy('topic_id')
                                    ->orderBy('order')
                                    ->get()
                                    ->mapWithKeys(fn (Concept $c) => [
                                        $c->id => ($c->topic?->unit?->grade ?? '?') . '. Sinif / ' . ($c->topic?->unit?->name ?? '-') . ' / ' . $c->name,
                                    ])
                                    ->all()
                            )
                            ->searchable()
                            ->native(false)
                            ->placeholder('Secmek zorunlu degil'),
                    ])
                    ->collapsed(),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('question_code')
                    ->label('Kod')
                    ->searchable(),
                Tables\Columns\TextColumn::make('quiz_type')
                    ->label('Tip')
                    ->badge(),
                Tables\Columns\TextColumn::make('difficulty')
                    ->label('Zorluk')
                    ->badge(),
                Tables\Columns\TextColumn::make('topic.name')
                    ->label('Unite')
                    ->formatStateUsing(fn ($state, $record) => $record->topic?->unit?->name ?? '-')
                    ->searchable(),
                Tables\Columns\TextColumn::make('order')
                    ->label('Sira')
                    ->sortable(),
            ])
            ->filters([
                Tables\Filters\TrashedFilter::make(),
            ])
            ->actions([
                Tables\Actions\ViewAction::make(),
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                    Tables\Actions\ForceDeleteBulkAction::make(),
                    Tables\Actions\RestoreBulkAction::make(),
                ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListQuestions::route('/'),
            'create' => Pages\CreateQuestion::route('/create'),
            'view' => Pages\ViewQuestion::route('/{record}'),
            'edit' => Pages\EditQuestion::route('/{record}/edit'),
        ];
    }

    public static function getEloquentQuery(): Builder
    {
        return parent::getEloquentQuery()
            ->with(['topic.unit', 'mcq', 'flashcard', 'fillBlank', 'matchingPairs'])
            ->withoutGlobalScopes([
                SoftDeletingScope::class,
            ]);
    }

    public static function mutateDataToTopic(array $data): array
    {
        $unitId = (int) ($data['topic_id'] ?? 0);
        $topic = UnitTopicResolver::defaultTopicForUnitId($unitId);
        if ($topic) {
            $data['topic_id'] = $topic->id;
        }

        return $data;
    }
}
